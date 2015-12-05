import csv
import datetime
import dateutil.parser
import pprint
import sys

schema = '''
CREATE TABLE "Indicators" (
    `FormID`    INTEGER NOT NULL,
    `Indicator`    TEXT NOT NULL,
    `Age`    TEXT,
    `Value`    INTEGER NOT NULL
);
CREATE TABLE `Forms` (
    `FormID`    INTEGER NOT NULL,
    `Date`    INTEGER NOT NULL,
    `Location`    TEXT NOT NULL,
    `TimeStart`    INTEGER NOT NULL,
    `TimeEnd`    INTEGER NOT NULL,
    `Team`    TEXT NOT NULL,
    `TimeReceivedOn`    INTEGER NOT NULL,
    PRIMARY KEY(FormID)
);
'''

form_mask = 'INSERT INTO `Forms` VALUES ({formid},{form_date},{location!r},{timeStart},{timeEnd},{team!r},{received_on});'

indicator_mask = 'INSERT INTO `Indicators` VALUES ({formid},{indicator!r},{age!r},{value});'

def totimestamp(datestr):
    return dateutil.parser.parse(datestr).timestamp()

def csv2sqlite(csv_path, f):
    f.write('BEGIN TRANSACTION;')
    f.write(schema)
    
    dates = set()
    
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['form_date'] = totimestamp(row['form_date'])
            row['timeStart'] = totimestamp(row['timeStart'])
            row['timeEnd'] = totimestamp(row['timeEnd'])
            row['received_on'] = totimestamp(row['received_on'])
            f.write(form_mask.format(**row))
            dates.add(row['form_date'])
            for key in [key for key in row if key.startswith('form|')]:
                form, indicator, age = key.split('|')
                d = {'formid': row['formid'],
                    'indicator': indicator,
                    'age': age,
                    'value': row[key] if len(row[key]) > 0 else 0}
                f.write(indicator_mask.format(**d))
                f.write('\n')
    f.write('COMMIT;')

if __name__ == '__main__':
    csv2sqlite(sys.argv[1], sys.stdout)
