from bse import BSE
import json

'''
How to use BSE.announcements get all announcements.

By default, only a single page of announcements is returned.

We increment the 'page_no' argument to paginate and get all announcements.

BSE can returns 2000+ announcements on a given day and result in 50+ requests.
'''

ann: list[dict] = []
total_count = 1000  # arbitary number to suppress pylint warnings
page_count = 1

with BSE() as bse:
    while True:
        # Returns Nth page of announcements for the day upto current time.
        res = bse.announcements(page_no=page_count)

        if page_count == 1:
            # ROWCNT is the total number of announcements for the day
            # We only need this once on first request
            total_count: int = res['Table1'][0]['ROWCNT']

        page_count += 1

        ann.extend(res['Table'])

        if len(ann) == total_count:
            break

        # Next two line are optional and prints percent completion status
        pct_completion = round(len(ann) / total_count * 100, 2)

        # Print on same line. \r is backspace to clear the previous print
        print(f'{pct_completion}%', flush=True, end='\r' * 8)

# Done save to file or anything else you need to do
with open('announcements.json', 'w') as f:
    json.dump(ann, f, indent=2)
