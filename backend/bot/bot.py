from bot.youtube_crawler import YoutubeCrawler

def main():
    # Example UUID for a user that should exist in the users table
    USER_ID = "3c30faa8-fe18-49f9-a283-5f26615902c9"

    # Initialize the crawler
    crawler = YoutubeCrawler(USER_ID)
    search_query = "python programming"

    try:
        # Try to load existing session from database
        if crawler.load_session():
            print("Successfully logged in using saved session!")
        else:
            print("No valid session found or session expired")
            # If no valid session, do manual login
            if not crawler.manual_login():
                print("Login failed. Exiting...")
                return

        # Proceed with search and video watching
        if crawler.search_query(search_query):
            print("Search successful")
            crawler.watch_videos(num_videos=3, watch_time_range=(10, 20))

        # Clean up old sessions periodically
        crawler.db.cleanup_old_sessions(days=30)
    except Exception as e:
        print(f"An error occurred during execution: {str(e)}")
    finally:
        crawler.close()


if __name__ == "__main__":
    main()
