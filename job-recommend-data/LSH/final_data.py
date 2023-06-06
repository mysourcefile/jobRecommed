import pandas as pd
import numpy as np
import re
import csv
import datetime
import os

# 각각 크롤링한 csv 불러오기
df1=pd.read_csv(r'C:\Users\Playdata\Desktop\programers_cp949_1.csv', encoding='cp949')
df2=pd.read_csv(r"C:\Users\Playdata\Desktop\wanted_cp949_1.csv", encoding='cp949')
df3=pd.read_csv(r"C:\Users\Playdata\Desktop\jumpit_cp949_2.csv", encoding='cp949')

# 직무&기술스택 보기
# 세 개의 CSV 파일 합치기
combined_position_stack = {}

# 첫 번째 CSV 파일 읽어오기
with open(r"C:\Users\Playdata\Desktop\position_stack1.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # 헤더 건너뛰기
    for row in reader:
        position = row[0]
        stack_item = row[1]
        if position in combined_position_stack:
            combined_position_stack[position].add(stack_item)
        else:
            combined_position_stack[position] = {stack_item}
            
# 두 번째 CSV 파일 읽어오기
with open(r"C:\Users\Playdata\Desktop\position_stack2.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # 헤더 건너뛰기
    for row in reader:
        position = row[0]
        stack_item = row[1]
        if position in combined_position_stack:
            combined_position_stack[position].add(stack_item)
        else:
            combined_position_stack[position] = {stack_item}

            
# 세 번째 CSV 파일 읽어오기
with open(r"C:\Users\Playdata\Desktop\position_stack3.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # 헤더 건너뛰기
    for row in reader:
        position = row[0]
        stack_item = row[1]
        if position in combined_position_stack:
            combined_position_stack[position].add(stack_item)
        else:
            combined_position_stack[position] = {stack_item}

#최종 저장
directory = r'C:\Users\Playdata\Desktop\\' 

filename1 = os.path.join(directory, 'combined_position_stack.csv')

with open(filename1, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Position', 'Stack'])  # 헤더 작성
    for position, stack in combined_position_stack.items():
        for stack_item in stack:
            writer.writerow([position, stack_item])


# 같은 공고 처리
# 프로그래머스와 원티드
df=pd.concat([df1,df2])

def preprocess_dataframe(df):
    df['공고명'] = df['공고명'].str.replace('벡엔드', '백엔드')
    df['회사명'] = df['회사명'].str.replace(r'\(.*?\)', '', regex=True).str.strip()
    return df

df1 = preprocess_dataframe(df1)
df2 = preprocess_dataframe(df2)
df3 = preprocess_dataframe(df3)
df=preprocess_dataframe(df)

intersection = pd.Series(list(set(df1['회사명'].unique()) & set(df2['회사명'].unique())))

filtered_df = df[df['회사명'].isin(intersection)]

# 공고명에서 '신입'과 ()로 둘러싸인 부분 삭제
filtered_df['공고명'] = filtered_df['공고명'].apply(lambda x: re.sub(r' \(신입.*?\)|신입|\[신입.*?\] |\[코스닥상장사\] |채용', '', x))
filtered_df['공고명'] = filtered_df['공고명'].apply(lambda x: re.sub(r'\(신입/경력\)', '', x))

pro_wanted_df = df[~df['링크'].isin(filtered_df['링크'])]

# 회사가 같고, 링크는 다르고, 한 공고문이 다른 공고문을 완전히 포함하고 있을 때 
# 중복된 공고명을 가진 그룹 찾기
grouped = filtered_df.groupby('회사명')

# 완전히 일치하는 경우를 찾는 코드
exact_match_df = pd.DataFrame(columns=filtered_df.columns)
for _, group in grouped:
    if len(group) > 1:
        for i in range(len(group)):
            prog_group = group.iloc[i]
            for j in range(i + 1, len(group)):
                wanted_group = group.iloc[j]
                if ((prog_group['링크'].startswith('https://programmers.co.kr') and wanted_group['링크'].startswith('https://www.wanted.co.kr'))
                    or (prog_group['링크'].startswith('https://www.wanted.co.kr') and wanted_group['링크'].startswith('https://programmers.co.kr'))):
                    if prog_group['공고명'].replace(" ", "") == wanted_group['공고명'].replace(" ", ""):
                        exact_match_df = exact_match_df.append(prog_group)
                        exact_match_df = exact_match_df.append(wanted_group)

# 포함관계인 경우를 찾는 코드
included_df = pd.DataFrame(columns=filtered_df.columns)
for _, group in grouped:
    if len(group) > 1:
        for i in range(len(group)):
            prog_group = group.iloc[i]
            for j in range(i + 1, len(group)):
                wanted_group = group.iloc[j]
                if ((prog_group['링크'].startswith('https://programmers.co.kr') and wanted_group['링크'].startswith('https://www.wanted.co.kr'))
                    or (prog_group['링크'].startswith('https://www.wanted.co.kr') and wanted_group['링크'].startswith('https://programmers.co.kr'))):
                    if (prog_group['공고명'].replace(" ", "") in wanted_group['공고명'].replace(" ", "") 
                    or wanted_group['공고명'].replace(" ", "") in prog_group['공고명'].replace(" ", "")):
                        included_df = included_df.append(prog_group)
                        included_df = included_df.append(wanted_group)

solo_df = filtered_df[~filtered_df['링크'].isin(exact_match_df['링크'])]
solo_df = solo_df[~solo_df['링크'].isin(included_df['링크'])]

# 원티드와 프로그래머스의 경우, 원티드를 대표로 함
exact_match_df = exact_match_df[exact_match_df['링크'].str.startswith('https://www.wanted.co.kr')]
included_df = included_df[included_df['링크'].str.startswith('https://www.wanted.co.kr')]

duplicates_df = pd.merge(exact_match_df, included_df, how='outer')

# solo_df를 더함
pro_wanted_df = pro_wanted_df.append(duplicates_df, ignore_index=True)

# filtered_results를 더함
pro_wanted_df = pro_wanted_df.append(solo_df, ignore_index=True)

pro_wanted_df.to_csv(r'C:\Users\Playdata\Desktop\pro_wanted_df.csv', index=False, encoding='cp949')

# 점핏까지
# df 합치기
df = pd.concat([pro_wanted_df, df3])
df =df.drop('Unnamed: 0',axis=1)
df['근무지'] = df['근무지'].str.replace('\n·', '')

intersection = pd.Series(list(set(pro_wanted_df['회사명'].unique()) & set(df3['회사명'].unique())))

filtered_df = df[df['회사명'].isin(intersection)]

# 공고명에서 '신입'과 ()로 둘러싸인 부분 삭제
filtered_df['공고명'] = filtered_df['공고명'].apply(lambda x: re.sub(r' \(신입.*?\)|신입|\[신입.*?\] |\[코스닥상장사\] |채용', '', x))
filtered_df['공고명'] = filtered_df['공고명'].apply(lambda x: re.sub(r'\(신입/경력\)', '', x))

final_df = df[~df['링크'].isin(filtered_df['링크'])]


# 회사가 같고, 링크는 다르고, 한 공고문이 다른 공고문을 완전히 포함하고 있을 때 
# 중복된 공고명을 가진 그룹 찾기
grouped = filtered_df.groupby('회사명')

# 완전히 일치하는 경우를 찾는 코드
exact_match_df = pd.DataFrame(columns=filtered_df.columns)
for _, group in grouped:
    if len(group) > 1:
        for i in range(len(group)):
            prog_group = group.iloc[i]
            for j in range(i + 1, len(group)):
                jumpit_group = group.iloc[j]
                if ((prog_group['링크'].startswith('https://programmers.co.kr') and jumpit_group['링크'].startswith('https://www.jumpit.co.kr'))
                    or (prog_group['링크'].startswith('https://www.jumpit.co.kr') and jumpit_group['링크'].startswith('https://programmers.co.kr'))):
                    if prog_group['공고명'].replace(" ", "") == jumpit_group['공고명'].replace(" ", ""):
                        exact_match_df = exact_match_df.append(prog_group)
                        exact_match_df = exact_match_df.append(jumpit_group)
for _, group in grouped:
    if len(group) > 1:
        for i in range(len(group)):
            wanted_group = group.iloc[i]
            for j in range(i + 1, len(group)):
                jumpit_group = group.iloc[j]
                if ((wanted_group['링크'].startswith('https://www.wanted.co.kr') and jumpit_group['링크'].startswith('https://www.jumpit.co.kr'))
                    or (wanted_group['링크'].startswith('https://www.jumpit.co.kr') and jumpit_group['링크'].startswith('https://www.wanted.co.kr'))):
                    if wanted_group['공고명'].replace(" ", "") == jumpit_group['공고명'].replace(" ", ""):
                        exact_match_df = exact_match_df.append(wanted_group)
                        exact_match_df = exact_match_df.append(jumpit_group)

# 포함관계인 경우를 찾는 코드
included_df = pd.DataFrame(columns=filtered_df.columns)
for _, group in grouped:
    if len(group) > 1:
        for i in range(len(group)):
            prog_group = group.iloc[i]
            for j in range(i + 1, len(group)):
                jumpit_group = group.iloc[j]
                if ((prog_group['링크'].startswith('https://programmers.co.kr') and jumpit_group['링크'].startswith('https://www.jumpit.co.kr'))
                    or (prog_group['링크'].startswith('https://www.jumpit.co.kr') and jumpit_group['링크'].startswith('https://programmers.co.kr'))):
                    if (prog_group['공고명'].replace(" ", "") in jumpit_group['공고명'].replace(" ", "") 
                    or jumpit_group['공고명'].replace(" ", "") in prog_group['공고명'].replace(" ", "")):
                        included_df = included_df.append(prog_group)
                        included_df = included_df.append(jumpit_group)
for _, group in grouped:
    if len(group) > 1:
        for i in range(len(group)):
            wanted_group = group.iloc[i]
            for j in range(i + 1, len(group)):
                jumpit_group = group.iloc[j]
                if ((wanted_group['링크'].startswith('https://www.wanted.co.kr') and jumpit_group['링크'].startswith('https://www.jumpit.co.kr'))
                    or (wanted_group['링크'].startswith('https://www.jumpit.co.kr') and jumpit_group['링크'].startswith('https://www.wanted.co.kr'))):
                    if (wanted_group['공고명'].replace(" ", "") in jumpit_group['공고명'].replace(" ", "") 
                    or jumpit_group['공고명'].replace(" ", "") in wanted_group['공고명'].replace(" ", "")):
                        included_df = included_df.append(wanted_group)
                        included_df = included_df.append(jumpit_group)

solo_df = filtered_df[~filtered_df['링크'].isin(exact_match_df['링크'])]
solo_df = solo_df[~solo_df['링크'].isin(included_df['링크'])]

# 원티드와 프로그래머스의 경우,점핏을 대표로 함
exact_match_df = exact_match_df[exact_match_df['링크'].str.startswith('https://www.jumpit.co.kr')]
included_df = included_df[included_df['링크'].str.startswith('https://www.jumpit.co.kr')]

duplicates_df = pd.merge(exact_match_df, included_df, how='outer')

# solo_df를 더함
final_df = final_df.append(duplicates_df, ignore_index=True)

# filtered_results를 더함
final_df = final_df.append(solo_df, ignore_index=True)


# 직무 전처리
df = final_df
df['직무'] = df['직무'].str.split(', ')
# 웹개발 하나만 있는 경우
df['직무'] = df['직무'].apply(lambda x: ["프론트엔드", "백엔드"] if isinstance(x, list) and x == ["웹개발"] else x)

# 웹개발이 포함되어 있는 경우 웹개발을 삭제
df['직무'] = df['직무'].apply(lambda x: [job for job in x if job != "웹개발"])

df.to_csv(r'C:\Users\Playdata\Desktop\df_pos.csv', index=False, encoding='cp949')
df=pd.read_csv(r'C:\Users\Playdata\Desktop\df_pos.csv', encoding='cp949')

df['직무'] = df['직무'].str.replace("'", '"')

# 기술스택 전처리
# 기술 스택 획일화
# np.where(condition, x, y)를 활용해서 condition이 참일 경우 x를, 아닌 경우 y로!
df['기술스택'] = df['기술스택'].str.replace("'", '"')
df['기술스택'] = np.where((df['기술스택'].isnull()) | (df['기술스택'] == "[]"), """[""]""", df['기술스택'])

# 마감일 전처리
# 마감일 전처리 
df['마감일'] = df['마감일'].str.replace('상시', '상시 채용')
df['마감일'] = df['마감일'].str.replace('채용 채용', '채용')
df['마감일'] = df['마감일'].fillna('상시 채용')

# 날짜 형식 2023-04-12
def format_date(date_str):
    if date_str.startswith('상시 채용'):
        return date_str
#     elif date_str.startswith('상시'):
#         return date_str
    elif ':' in date_str:
        date_obj = datetime.datetime.strptime(date_str, '%y년 %m월 %d일 %H:%M까지')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        return formatted_date
    else:
        return date_str

df['마감일'] = df['마감일'].apply(format_date)

# # 날짜 형식 2023-04-12 00:00
# import datetime

# def format_date(date_str):
#     if date_str.startswith('상시 채용'):
#         return date_str
#     elif ':' in date_str:
#         date_obj = datetime.datetime.strptime(date_str, '%y년 %m월 %d일 %H:%M까지')
#         formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
#         return formatted_date
#     else:
#         date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
#         formatted_date = date_obj.strftime('%Y-%m-%d') + ' 24:00'
#         return formatted_date

# df['마감일'] = df['마감일'].apply(format_date)

# 근무지
df['근무지'] = df['근무지'].str.replace('주소 ', '')
df['근무지'] = df['근무지'].str.replace('대한민국 ', '')
df['근무지'] = df['근무지'].str.replace('서울특별시', '서울')
df['근무지'] = df['근무지'].str.replace('서울시', '서울')
df['근무지'] = df['근무지'].str.replace('경기도', '경기')
df['근무지'] = df['근무지'].str.replace('제주특별자치도', '제주')
df['근무지'] = df['근무지'].str.replace('제주특별자치도', '제주')
df['근무지'] = df['근무지'].str.replace('울산광역시', '울산')
df['근무지'] = df['근무지'].str.replace('경상북도', '경북')
df['근무지'] = df['근무지'].str.replace('부산광역시', '부산')
df['근무지'] = df['근무지'].str.replace('인천광역시', '인천')
df['근무지'] = df['근무지'].str.replace('대전시', '대전')
df['근무지'] = df['근무지'].str.replace('대전광역시', '대전')
df['근무지'] = df['근무지'].str.replace('대구광역시', '대구')
df['근무지'] = df['근무지'].str.replace('서울 경기', '경기')
df['근무지'] = df['근무지'].str.replace('전라남도', '전남')
df['근무지'] = df['근무지'].str.replace('인천시', '인천')


# 따로 열어보고 이상한 것 적는 곳
df['근무지'] = df['근무지'].str.replace('Level ', '')
df['근무지'] = df['근무지'].str.replace('입니다', '')
df['근무지'] = df['근무지'].str.replace('입니다', '')
df['근무지'] = df['근무지'].str.replace('대구 대전', '대전')
df['근무지'] = df['근무지'].str.replace('서울 06237', '')
df['근무지'] = df['근무지'].str.replace(' 서울', '서울')
df['근무지'] = df['근무지'].str.replace(r'서울 \(06159\)\s*', '')
df['근무지'] = df['근무지'].str.replace(r'서울 13449\)\s*', '')
df['근무지'] = df['근무지'].str.replace(r'\(07807\)\s*', '')
df['근무지'] = df['근무지'].str.replace(r'\(08380\)\s*', '')
df['근무지'] = df['근무지'].str.replace(r'\(06159\)\s*', '')
df['근무지'] = df['근무지'].str.replace(r'\[본사\]\s*', '')
df['근무지'] = df['근무지'].str.replace('\n·', '')
df['근무지'] = df['근무지'].str.replace(r'^\(\d+\)\s*', '', regex=True)
df['근무지'] = df['근무지'].str.replace(r'\[.*?\]', '', regex=True)
df['근무지'] = df['근무지'].str.replace('연남로13길9', '서울 마포구 연남로13길9', regex=True)
df['근무지'] = df['근무지'].str.replace('광주 광주광역시', '광주')
df['근무지'] = df['근무지'].str.replace('서울 논현로', '서울 강남구 논현로')
df['근무지'] = df['근무지'].str.replace('서울 왕십리로', '서울 성동구 왕십리로')
# df['근무지'] = df['근무지'].str.replace('서울 대치로', '')
df['근무지'] = df['근무지'].str.replace('서울 서초동', '서울 서초구 서초동')
df['근무지'] = df['근무지'].str.replace('서울 마포대로', '서울 마포구 마포대로')
# df['근무지'] = df['근무지'].str.replace('서울 강남대로', '')
df['근무지'] = df['근무지'].str.replace('서울 반포대로', '서울 서초구 반포대로')
df['근무지'] = df['근무지'].str.replace('서울 원격 근무', '원격 근무')
df['근무지'] = df['근무지'].str.replace('서울 개포로', '서울 강남구 개포로')
df['근무지'] = df['근무지'].str.replace('서울 삼성로', '서울 강남구 삼성로')
df['근무지'] = df['근무지'].str.replace('서울 여의도', '서울 영등포구 여의도동')
df['근무지'] = df['근무지'].str.replace('서울서울', '서울')
df['근무지'] = df['근무지'].str.replace('서울 선릉로', '서울 강남구 선릉로')
df['근무지'] = df['근무지'].str.replace('서울 테헤란로', '서울 강남구 테헤란로')
df['근무지'] = df['근무지'].str.replace('서울 삼성동', '서울 강남구 삼성동')
df['근무지'] = df['근무지'].str.replace('서울 양재동', '서울 서초구 양재동')
df['근무지'] = df['근무지'].str.replace('경기 금토로', '경기 성남시 수정구 금토로')
df['근무지'] = df['근무지'].str.replace('대전 가정북로', '대전 유성구 가정북로')
df['근무지'] = df['근무지'].str.replace('서울 강남대로 156', '서울 서초구 강남대로 156')
df['근무지'] = df['근무지'].str.replace('경기 판교', '경기 성남시 분당구 판교동')
df['근무지'] = df['근무지'].str.replace('대구 대구시내', '대구 중구 동성로')
df['근무지'] = df['근무지'].str.replace('서울 양화로', '서울 마포구 양화로')
df['근무지'] = df['근무지'].str.replace('서울 발산역', '서울 강서구 마곡동')
df['근무지'] = df['근무지'].str.replace('서울 양재역', '서울 서초구 양재역')
# '근무지' 컬럼의 데이터 형식 변경
df.loc[df['근무지'].str.contains('Seoul, Republic of Korea', na=False), '근무지'] = None
df.loc[df['근무지'].str.contains('서울 대치로 223', na=False), '근무지'] = None
df.loc[df['근무지'].str.contains('원격 근무', na=False), '근무지'] = None
df.loc[df['근무지'].str.contains('onetkorea137@gmail.com', na=False), '근무지'] = None

df.dropna(subset=['근무지'], inplace=True)  # 결측치 가진 데이터 삭제
df['근무지'] = df['근무지'].astype(str)  # 데이터 타입을 문자열로 변환


df['근무지'] = df['근무지'].apply(lambda x: x.split(' ', 1)[1] if len(x.split(' ')) > 1 and x.split(' ')[0] == x.split(' ')[1] else x)


# 저장
df.to_csv(r'C:\Users\Playdata\Desktop\final_true.csv', index=True, encoding='cp949')