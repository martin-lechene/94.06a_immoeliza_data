from scraper.scraper import Immoweb_Scraper
import time


def main():
    max = 333
    print(
        "Welcome to Immoweb Scraper!\n"
        "Enter how many pages you want to scrape (max 333 pages)"
    )
    numpages = int(input("Enter number of pages:  "))
    if numpages > max:
        exit(
            f"You have exceeded the maximum of scrapeable pages. Choose a number lower than {max}"
        )
    else:
        start = time.time()
        immoscrap = Immoweb_Scraper(numpages + 1)
        immoscrap.scrape_table_dataset()
        immoscrap.update_dataset()
        immoscrap.Raw_DataFrame()
        immoscrap.to_csv_raw()
        immoscrap.Clean_DataFrame()
        immoscrap.to_csv_clean()
        end = time.time()
        print("Time Taken: {:.6f}s".format(end - start))
        print(
            f"for {len(immoscrap.data_set_df)} rows on {immoscrap.numpages } scraped base urls"
        )
        exit("Thank you for using Immoweb Scraper!")


if __name__ == "__main__":
    main()
