import os
import sys
import time
import math
import queue
import tweepy
import pandas as pd
import concurrent.futures
from collections import deque
from typing import List, Optional, Iterable

sys.path.append("...")

from dotenv import load_dotenv
from more_itertools import chunked

from alerts.logger import logger
load_dotenv()


class TwitterScraperClient:
    ''' 
    Using concurrency to distribute our API rates throughout different User Applications and to reduce response delay overhead when getting data
    Also allows for API Key rotation

    Used methods are those starting with: iter_....
    '''

    def __init__(self, api_keys: int):
        self.client_count = 0  # Logs the number of clients created
        self.n = api_keys  # Number of twitter keys to use

        self.auth_keys = self._get_auth_keys(self.n)
        self.clients = self.create_thread_clients(self.auth_keys)
        self._client_rotator = deque(
            enumerate(self.clients, start=1))  # Create a queue

    def create_thread_clients(self, auth_keys) -> list:
        """ Creates the Twitter Client Instances using concurrency (speeds up client creation)
        ...
        """
        clients = []
        # Create the number of clients = number of twitter keys + 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.n + 1) as executor:
            futures = []
            # For the twitter keys within
            for consumer_key, consumer_secret, twitter_secret_token, twitter_access_token in zip(auth_keys['CONSUMER_KEY'], auth_keys['CONSUMER_SECRET'], auth_keys['SECRET_ACCESS_TOKEN'], auth_keys['ACCESS_TOKEN']):
                job = executor.submit(  # Submit the job into each executor
                    self._create_tweepy_client,  # Create a tweepy client in each pool worker
                    consumer_key=consumer_key,
                    consumer_secret=consumer_secret,
                    twitter_secret_token=twitter_secret_token,
                    twitter_access_token=twitter_access_token,
                )
                self.client_count += 1
                futures.append(job)  # Append the job into futures

            for client_num, future in enumerate(concurrent.futures.as_completed(futures), start=1):
                client = future.result()
                logger.info(f"Client number {client_num} initialized.")
                # Append the worker into the clients list
                clients.append(client)
        return clients

    ''' Client Creation Methods '''
    @staticmethod
    def _get_auth_keys(n):
        """ Get the Authentication Keys for each token in the form of dict, with list values
        ...
        """
        auth_keys = {'CONSUMER_KEY': [], 'CONSUMER_SECRET': [
        ], 'SECRET_ACCESS_TOKEN': [], 'BEARER_TOKEN': [], 'ACCESS_TOKEN': []}
        for i in range(1, n+1):
            auth_keys['CONSUMER_KEY'].append(
                os.environ.get("TWITTER_CONSUMER_KEY_" + str(i)))
            auth_keys['CONSUMER_SECRET'].append(
                os.environ.get("TWITTER_CONSUMER_SECRET_" + str(i)))
            auth_keys['SECRET_ACCESS_TOKEN'].append(
                os.environ.get("TWITTER_SECRET_ACCESS_TOKEN_" + str(i)))
            auth_keys['BEARER_TOKEN'].append(
                os.environ.get("TWITTER_BEARER_TOKEN_" + str(i)))
            auth_keys['ACCESS_TOKEN'].append(
                os.environ.get("TWITTER_ACCESS_TOKEN_" + str(i)))
        return auth_keys

    @staticmethod
    def _create_tweepy_client(consumer_key: str, consumer_secret: str, twitter_secret_token: str, twitter_access_token: str):
        """ Creates a tweepy client instance, provides access to API endpoints 
        """
        try:
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(twitter_access_token, twitter_secret_token)
            api = tweepy.API(auth, wait_on_rate_limit=False)
            return api
        except Exception as e:
            raise logger.exception(e)

    ''' Exception handling '''

    @staticmethod
    def _get_rate_limits(client, relationship_type) -> dict:
        """ Return the rate limit status of a particular endpoint 
        Sample Return: {'limit': 15, 'remaining': 0, 'reset': 1635351540}
        """
        if relationship_type == "followers":
            limits = client.rate_limit_status(
            )["resources"]["followers"]["/followers/ids"]
        elif relationship_type == "followings":
            limits = client.rate_limit_status(
            )["resources"]["friends"]["/friends/ids"]
        else:
            raise NotImplementedError
        return limits

    ''' Endpoint Methods '''

    def iter_processed_userinfo(
        self,
        screen_names: List[str],
        user_ids: List[int],
        chunk_size: Optional[int] = None,
    ) -> Iterable[pd.DataFrame]:
        """ Given a list of names(as strings), it returns user data 
        screen_names : list of usernames in string
        user_ids : list of userids in integer
        """

        def process_user_infos(user_identities):
            required_keys = ['id', 'screen_name', 'followers_count',
                             'friends_count', 'created_at', 'description', 'url', 'location']
            rename_columns = {'id': 'user_id', 'screen_name': 'user_name', 'friends_count': 'followings_count',
                              'url': 'user_link', 'location': 'user_location', 'description': 'user_description', 'created_at': 'user_created_at'}

            user_infos = pd.DataFrame(list(map(lambda x: [
                                      x._json[key] for key in required_keys], user_identities)), columns=required_keys)
            user_infos = user_infos.rename(columns=rename_columns)
            return user_infos

        iterable_raw_users = self.iter_raw_users(
            screen_names=screen_names, user_ids=user_ids
        )

        if chunk_size is None:
            processed_user = process_user_infos(iterable_raw_users)
            yield processed_user
        else:
            chunked_raw_users = chunked(iterable_raw_users, chunk_size)
            for user_chunk in chunked_raw_users:
                logger.info("Processing user")
                processed_user = process_user_infos(user_chunk)
                yield processed_user

    def iter_processed_followings(
        self,
        screen_names: List[str] = None,
        user_ids: List[int] = None,
        chunk_size: Optional[int] = 10_000,
        upper_limit: int = None,
    ):
        """ Given a list of names(as strings), it returns user data 
        screen_names : list of usernames in string
        user_ids : list of userids in integer
        """
        def process_followings(user_followers):
            try:
                followings_df = pd.DataFrame(
                    user_followers, columns=[
                        "twitter_follower_id", "twitter_followee_id"]
                )
                return followings_df
            except Exception as e:
                logger.error(
                    f"Process Followings: Error occured while processing data, {e}")
                return None

        user_followings_iter = self.iter_follows(
            relationship_type="followings",
            user_ids=user_ids,
            screen_names=screen_names,
            upper_limit=upper_limit,
        )

        user_following_pairs = (
            (user, following)
            for user, followings_iter in user_followings_iter
            for following in followings_iter
        )

        if chunk_size is None:
            followings_df_batch = process_followings(user_following_pairs)
            yield followings_df_batch
        else:
            for chunked_user_following_pairs in chunked(user_following_pairs, chunk_size):
                try:
                    followings_df_batch = process_followings(
                        chunked_user_following_pairs)
                except Exception as e:
                    logger.error(
                        f"Twitter followings: Error occured while extracting data, user account is private.")
                yield followings_df_batch

    def iter_processed_followers(
        self,
        screen_names: List[str] = None,
        user_ids: List[int] = None,
        chunk_size: Optional[int] = None,
        upper_limit: int = None,
    ):

        def process_followers(user_followers):
            try:
                followers_df = pd.DataFrame(
                    user_followers, columns=[
                        "twitter_followee_id", "twitter_follower_id"]
                )
                return followers_df
            except Exception as e:
                logger.error(
                    f"Process Followers: Error occured while processing data, {e}")
                return None

        user_followers_iter = self.iter_follows(
            relationship_type="followers",
            user_ids=user_ids,
            screen_names=screen_names,
            upper_limit=upper_limit,
        )
        try:
            user_follower_pairs = (
                (user, follower)
                for user, followers_iter in user_followers_iter
                for follower in followers_iter
            )
            if chunk_size is None:
                followers_df_batch = process_followers(user_follower_pairs)
                yield followers_df_batch
            else:
                for chunked_user_follower_pairs in chunked(user_follower_pairs, chunk_size):
                    followers_df_batch = process_followers(
                        chunked_user_follower_pairs)
                    yield followers_df_batch
        except Exception as e:
            logger.error(
                f"Twitter followers: Error occured while extracting data, {e}")
            pass

    ''' Processing Pipelines '''

    def iter_follows(
        self,
        screen_names: List[str] = None,
        user_ids: List[int] = None,
        relationship_type: str = None,
        upper_limit: int = None,
    ):
        ''' Middleman function that connects iter_processed_followers, the actual function we will call for the user followers, with iter_follower_followings

        Parameters
        =============
        screen_names -> List[str]       : List containing screen names, can be found beside the @
        user_ids -> List[str]           : List containing user ids
        relationship_type -> [str]      : String describing the relationship type of either "followers" or "followings"

        Rate Limits
        =============
        Refer to face function iter_processed_followers, iter_processed_followings

        Outputs
        =============
        Iterable[(user, relation_ids, )]        : (defining user detail (user_id or screen_name), relation_ids the returned result from the twitter api)

        Example Usage
        =============
        >>> user_followings_iter = self.iter_follows(relationship_type="followings", user_ids=user_ids, screen_names=screen_names, upper_limit=upper_limit, )
        '''
        user_id_or_screen_name, users_of_interest = (
            ("user_id", user_ids)
            if user_ids is not None
            else ("screen_name", screen_names)
        )

        TOTAL_USERS = len(users_of_interest)

        logger.info(
            f"Twitter {relationship_type}: Start extraction for {TOTAL_USERS} users.")

        for user_num, user in enumerate(users_of_interest, start=1):
            relation_ids = self.iter_follower_following(
                relationship_type, **{user_id_or_screen_name: user}
            )
            yield user, relation_ids
            logger.info(
                f"Twitter {relationship_type}: {user_num}/{TOTAL_USERS} users extracted.")

        logger.info(
            f"Twitter {relationship_type}: Completed extraction for "
            f"{TOTAL_USERS} users."
        )

    def iter_raw_users(
        self,
        screen_names: List[str],
        user_ids: List[int],
    ) -> Iterable[dict]:

        users_of_interest = user_ids if user_ids is not None else screen_names

        CHUNK_SIZE = 100
        TOTAL_USERS = len(users_of_interest)
        TOTAL_BATCHES = math.ceil(TOTAL_USERS / CHUNK_SIZE)
        logger.info(
            f"Twitter User Details: Getting user details for "
            f"{TOTAL_USERS} users in {TOTAL_BATCHES} batches of {CHUNK_SIZE}"
        )

        ids_or_names_queue = queue.SimpleQueue()
        for ids_or_names_chunk in chunked(users_of_interest, CHUNK_SIZE):
            ids_or_names_queue.put_nowait(ids_or_names_chunk)
        while not ids_or_names_queue.empty():
            logger.info(
                "Twitter User Details: Starting threads for extraction")
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(self.clients) + 1
            ) as executor:
                futures = []
                for client_num, tw_client in enumerate(self.clients, start=1):
                    if ids_or_names_queue.empty():
                        break
                    ids_or_names = ids_or_names_queue.get_nowait()
                    job = (
                        executor.submit(
                            tw_client.lookup_users,
                            user_id=ids_or_names,
                        )
                        if user_ids is not None
                        else executor.submit(
                            tw_client.lookup_users,
                            screen_name=ids_or_names,
                        )
                    )

                    futures.append(job)

                    batch_num = TOTAL_BATCHES - ids_or_names_queue.qsize()

                    logger.info(
                        f"Twitter User Details: Sent {len(ids_or_names)} "
                        f"posts, "
                        f"{batch_num}/{TOTAL_BATCHES} total batches, "
                        f"using key number {client_num}."
                    )
                for future in concurrent.futures.as_completed(futures):
                    resp = future.result()
                    yield from resp
            logger.info(
                "Twitter User Details: Fetched some results, closing threads.")
        logger.info("Twitter User Details: Fetched all results")

    def iter_follower_following(self,
                                relationship_type: str,
                                user_id=None,
                                screen_name=None,
                                upper_limit: int = None,
                                cursor=None,):
        """ Returns an iterator with the userids, for followers of the given user - user_followers that the given user follows - user_followings
        """
        def target_user_function(client, relationship_type):
            """ Returns a function based on root level endpoint call
            """
            if relationship_type == "followers":
                return client.get_follower_ids
            elif relationship_type == "followings":
                return client.get_friend_ids
            else:
                raise ValueError(
                    "Enter a valid relationship type, either 'followers' or 'following'!")

        user_id_or_screen_name, identifier = (
            ("user_id", user_id) if user_id is not None else ("screen_name", screen_name))

        user_str = f"{user_id_or_screen_name}: {identifier}"

        logger.info(
            f"Twitter {relationship_type}: Starting extraction for {user_str}.")

        cursor = cursor or -1  # Start at first page if cursor is None
        client_index, client = self._client_rotator[0]  # Get the latest client
        target_f = target_user_function(client, relationship_type)

        self.id_count, ids, page_count = 0, 0, 1  # log the number of ids scraped

        while cursor:
            try:
                # Handle rate limit errors
                for attempt_num in range(1, self.n + 2):
                    try:
                        logger.info(
                            f"Twitter {relationship_type}: Client {client_index}. Extracting for {user_str}, page {page_count}. Cursor target id {cursor}")
                        if not user_id:  # If user_id == None
                            ids, (prev_cursor, cursor) = target_f(
                                screen_name=screen_name, cursor=cursor,)
                            # Log the number of users extracted
                            self.id_count += len(ids)
                        else:
                            ids, (prev_cursor, cursor) = target_f(
                                user_id=user_id, cursor=cursor,)
                            # Log the number of users extracted
                            self.id_count += len(ids)

                        if upper_limit is not None:
                            if self.id_count >= upper_limit:
                                cursor = 0
                                logger.info(
                                    f"Stopping extraction at {upper_limit}th mark"
                                )
                        break
                    except tweepy.TooManyRequests:  # If rate limit error hit
                        # Switch to next client if rate limit reached
                        if attempt_num <= self.n:
                            prev_client_index = client_index
                            # Rotate deque to switch first client.
                            self._client_rotator.rotate(-1)
                            client_index, client = self._client_rotator[0]
                            logger.info(
                                f"Twitter {relationship_type}: Rate limit reached for client {prev_client_index}, switching to client {client_index}. {self.id_count} user ids scraped with this client.")
                            # Get new client's target function.
                            target_f = target_user_function(
                                client, relationship_type)
                        # If subsequent client also rate limited, wait for
                        # reset.
                        elif attempt_num > self.n:
                            limits = self._get_rate_limits(
                                client, relationship_type)
                            reset_time = limits["reset"]
                            curr_time = int(time.time())
                            # 2 second waiting buffer
                            sleep_for = int(
                                max(reset_time - curr_time + 2, 0))  # Allow rates to recover
                            logger.info(
                                f"Twitter {relationship_type}: Rate limit reached for all clients, sleeping for {sleep_for}s while limits recover.")
                            time.sleep(sleep_for)
                        else:  # Should not reach here, but handle just in case
                            logger.error(
                                f"Twitter {relationship_type}: Unexpected error")
                            ids = []

                yield from ids  # Create iterable

            # Skip as long as tweep error occurs
            except Exception:
                # Unknown Errors
                logger.exception(
                    f"Twitter {relationship_type}: Skipping extraction for {user_str}, unexpected error occurred.")
                ids = []
                break

            page_count += 1

        logger.info(
            f"Twitter {relationship_type}: Completed extraction for {user_str}. {self.id_count} users extracted")
