import pandas as pd 
import streamlit as st 
from sklearn.metrics.pairwise import haversine_distances
from math import radians

flatten_list=lambda l:[x for xl in l for x in xl]
def plz_distance(src,dest):
    src_in_radians = [radians(_) for _ in src]
    dest_in_radians = [radians(_) for _ in dest]
    result = haversine_distances([src_in_radians, dest_in_radians])[0][1]
    return result * 6371000/1000  # multiply by Earth radius to get kilometers


post_codes = pd.read_csv('swiss_plzs.tsv',sep='\t',header=None)
charities = pd.read_csv('charities.tsv',sep='\t')
charities['Accepted Items'] = charities['Accepted Items'].str.split(',')
#post_codes['postal_area'] = post_codes[1].astype('str') + ' ' + post_codes[2]

postal_codes = [''] + list(post_codes[0].unique())

coordinates = dict({})
for i,row in post_codes.iterrows():
    coordinates[str(row[0])[0:4]] = [row[1],row[2]]
coordinates['3001'] = coordinates['3004'] #Fix some missing postal codes

item_types = (list(set(flatten_list(list(charities['Accepted Items'])))))
item_types = [s.strip() for s in item_types]


st.set_page_config(page_title='Where2Give: Find the closest location where you can give away your spare items for charitable use',layout='wide')
st.title('Where2Give: Find the closest location where you can give away your spare items for charitable use')
st.markdown(""" ### Introduction
It happens more than often that we have spare items or canned food that we no longer use, and on the other hand don't think at all they should be thrown away. I have always had difficulty finding 
the right organisation to donate spare items, which is also closeby. Therefore, I decided to create a database of all places in Switzerland where you can donate (canned) food, 
household appliances, furniture, and other non-monetary items. Please help complete this database by going to https://github.com/aghasemi/where2give and adding new organisations to the file 
`charities.tsv`.

Here you can find the location closest to you by searching for a certain postal code and the item you want to dontate. 
""")
post_code = st.selectbox('Please choose a postal code', options=postal_codes, index = 0)
items = st.multiselect('What do you want to give away?',options=item_types,default=item_types)

if len(post_code)>0:
    plz = post_code[0:4]
    plz_coords = coordinates[plz]
    charities['distance'] = charities['PLZ'].apply(lambda c_plz: plz_distance(plz_coords,coordinates.get(str(c_plz),[47,8])) )
    result_df = charities[charities.apply(lambda row: any([x in row['Accepted Items'] for x in items]),axis=1)].sort_values(by='distance',ascending=True)
    result =''
    for i,row in result_df.head(10).iterrows():
        result += f"* _{row['distance']:2.1f} km_. [{row['Name']}]({row['Website']}), {row['Address']}. Accepts __{','.join(row['Accepted Items'])}__\n"
    st.markdown(result)



