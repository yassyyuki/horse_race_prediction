from race_index import *
from race_record_netkeiba import *

ID = '202205020101'

def main():
    race_index_df = get_race_index_df(ID)
    race_record_df = get_race_record_df(ID)
    merged_df = pd.merge(race_index_df, race_record_df, left_on='hourse_number', right_on='馬番')
    merged_df.to_excel(f'race_record{ID}.xlsx', index = False)
if __name__ == '__main__':
    main()