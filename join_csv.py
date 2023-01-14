# Code borrowed from stack overflow: 
# https://stackoverflow.com/questions/42092263/combine-multiple-csv-files-into-a-single-xls-workbook-python-3

import pandas as pd
import sys
import os


def main(output_file, *input_files):
    with pd.ExcelWriter(output_file) as writer:
        for filepath in input_files:
            df = pd.read_csv(filepath)
            sheet_name = ' '.join(
                    s.capitalize() for s in os.path.splitext(
                        os.path.basename(filepath)
                        )[0].split('-'))
            df.to_excel(writer, index=False, sheet_name=sheet_name)
    print('Written: {}\nInput Files:\n\t{}\n'.format(output_file, '\n\t'.join(input_files)))


if __name__ == '__main__':
    main(*sys.argv[1:])

