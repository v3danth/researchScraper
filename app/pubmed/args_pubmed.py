import datetime

# from mailer import send_scrape_email
# from pubmed_5 import run_spider
# import subprocess TODO: add parallelism to run_spider

from app.mailer import send_scrape_email
from app.pubmed.pubmed_5 import run_spider


def get_biweekly_dates(start_year, end_year):
    biweekly_dates = []
    for year in range(start_year, end_year + 1):
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
        current_date = start_date

        while current_date <= end_date:
            biweekly_dates.append((current_date, current_date + datetime.timedelta(days=1)))
            current_date += datetime.timedelta(days=1)

    biweekly_list = [
        f"{start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')}"
        for start_date, end_date in biweekly_dates
    ]
    return biweekly_list


def get_daily_date_ranges(start_year, end_year):
    ranges = []
    for year in range(start_year, end_year + 1):
        current = datetime.date(year, 1, 1)
        end = datetime.date(year, 12, 31)

        while current <= end:
            ranges.append(
                (
                    current.strftime("%Y/%m/%d"),
                    (current + datetime.timedelta(days=1)).strftime("%Y/%m/%d"),
                )
            )
            current += datetime.timedelta(days=1)

    return ranges

def pubmed_main_scarper(keyword, title, abstract, start_year, end_year, mailer_flag=False):
    output_path = f"PubMed_Output_{title}_{keyword}_{abstract}_{start_year}_{end_year}.csv"

    # create empty file
    open(output_path, "w").close()

    for start_date, end_date in get_daily_date_ranges(start_year, end_year):
        try:
            run_spider(
                article_title=title,
                article_keyword=keyword,
                article_abstract=abstract,
                start_date=start_date,
                end_date=end_date,
                file_name=output_path,
            )
            print(f"Success: {start_date} - {end_date}")
            mailer_flag = True

        except Exception as e:
            print(f"Failed: {start_date} - {end_date}")
            print(e)

    if mailer_flag:
        send_scrape_email(output_path)


if __name__ == "__main__":
    keyword = input("Article Keyword: ")
    title = input("Article Title: ")
    abstract = input("Article Abstract: ")
    start_year = int(input("Start year: "))
    end_year = int(input("End year: "))
    pubmed_main_scarper(keyword, title, abstract, start_year, end_year)
