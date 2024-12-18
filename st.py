## requirements
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json

## 페이지탭 설정
st.set_page_config(
    page_title='아파트 수요공급 대시보드', # 페이티탭 제목
    page_icon='🏬', # 페이지탭 아이콘
    layout='wide', # 넓은 레이아웃
    initial_sidebar_state='expanded' # 확장된 상태에서 사이드바 표시
)


## 어두운 테마 설정
alt.themes.enable('dark')


## 데이터 불러오기
dt = pd.read_csv('apt_sale.csv')


## 사이드바 설정
with st.sidebar:
    st.title('🏬 아파트 수요공급 대시보드') # 사이드바 제목

    year_list=list(dt.year.unique())[::-1] # 년도 리스트 추출

    sel_year=st.selectbox('년도를 선택하세요 !',year_list,index=0) # 년도 select box
    dt_sel_year=dt[dt.year==sel_year] # 년도별 하위집합 설정
    dt_sel_year_sorted=dt_sel_year.sort_values(by='value',ascending=False) # 정렬

    category_list=list(dt.category.unique())[::-1] # 카테고리 리스트 추출

    sel_category=st.selectbox('항목을 선택하세요 !',category_list,index=2) # 카테고리 select box
    dt_sel_category=dt[dt.category==sel_category] # 카테고리별 하위집합 설정

    col_theme_list=['greens','blues','cividis','inferno','magma','plasma','reds','rainbow','turbo','viridis'] # 색상 리스트 설정
    sel_col_theme=st.selectbox('테마 색상을 고르세요 !',col_theme_list) # 색상 select box


## heatmap 지도 설정

# 초기분양률 heatmap
pre_sale_rate='초기분양률'
dt_pre=dt.query('category==@pre_sale_rate') # 카테고리의 초기분양률만 이용

heatmap_pre=alt.Chart(dt_pre).mark_rect().encode(
    y=alt.Y(
        'year:O', # Y=연도:명목
        axis=alt.Axis(
            title=None # 제목없음
        )),
    x=alt.X(
        'city:O', # X=도시:명목
        axis=alt.Axis(
            title=None, # 제목없음
            labelAngle=0 # X label 가로
        )),
    color=alt.Color(
        'max(value):Q', # 색=값:수치
        legend=alt.Legend(
            title="",
            orient='right'), # 레전드 오른쪽 위치
        scale=alt.Scale(scheme=sel_col_theme)), # 색상 select box 이용
    stroke=alt.value('black'), # 선 검정
    strokeWidth=alt.value(0.25), # 선 넓이
    tooltip=[
        alt.Tooltip('year:O',title='연도'), # 툴팁 설정
        alt.Tooltip('value:Q',title='값')
    ]
).properties(
    width=900 # 넚이
).configure_legend(
    titleFontSize=16,
    labelFontSize=14,
    titlePadding=0
).configure_axisX(
    labelFontSize=14
).configure_axis(
    labelFontSize=12,
    titleFontSize=12
)

# 공급부담지표 heatmap
sale_supply_rate='공급부담지표'
dt_ss=dt.query('category==@sale_supply_rate') # 카테고리의 공급부담지표만 이용

heatmap_ss=alt.Chart(dt_ss).mark_rect().encode(
    y=alt.Y(
        'year:O',
        axis=alt.Axis(
            title=None
        )),
    x=alt.X(
        'city:O',
        axis=alt.Axis(
            title=None,
            labelAngle=0
        )),
    color=alt.Color(
        'max(value):Q',
        legend=alt.Legend(
            title="",
            orient='right'),
        scale=alt.Scale(scheme=sel_col_theme)),
    stroke=alt.value('black'),
    strokeWidth=alt.value(0.25),
    tooltip=[
        alt.Tooltip('year:O',title='연도'),
        alt.Tooltip('value:Q',title='값')
    ]
).properties(
    width=900
).configure_legend(
    titleFontSize=16,
    labelFontSize=14,
    titlePadding=0
).configure_axisX(
    labelFontSize=14
).configure_axis(
    labelFontSize=12,
    titleFontSize=12
)


## choropleth 지도 설정
korea_city=json.load(
    open('korea_city_modified.json',encoding='UTF-8') # geojson 불러오기
)

dt_year_target=dt.query('year==@sel_year&category==@sel_category') # year,category값 selectbox 이용

choropleth=px.choropleth_mapbox(
    dt_year_target, # 데이터
    geojson=korea_city, # 지도데이터
    locations='city', # 데이터 패딩값
    featureidkey='properties.CTP_KOR_NM', # 지도데이터 패딩값
    mapbox_style='carto-darkmatter', # 스타일
    zoom=5, # 줌
    center={'lat':35.9,'lon':126.98}, # 경위도=한국
    color='value', # 색=값
    color_continuous_scale=sel_col_theme, # 테마색 selectbox 이용
    range_color=(0,max(dt_year_target['value'])), # 값 범위 0 ~ value 최대값
    opacity=1, # 투명도 없음
    labels={'value':'값','city':'시도명'}, # 라벨링
    hover_data=['city','value'] # 마우스 호버 값
)
choropleth.update_geos(
    fitbounds='locations', # 지도 범위와 데이터 위치 일치 조정
    visible=False # 축 숨기기
)
choropleth.update_layout(
    template='plotly_dark', # 다크 테마
    plot_bgcolor='rgba(0,0,0,0)', # 플롯 배경 투명
    paper_bgcolor='rgba(0,0,0,0)', # 플롯 외부 배경 투명
    margin=dict(l=0,r=0,t=0,b=0), # 플롯 외부 여백 0
    height=400, # 높이
    width=1000 # 너비
)


## donutchart

# 차이함수 설정
def cal_presale_diff(dt, year, target):
    sel_year_dt=dt.query('year==@sel_year&category==@sel_category').reset_index() # selectbox 이용
    before_year_dt=dt.query('year==@sel_year-1&category==@sel_category').reset_index() # -1로 이전년도
    sel_year_dt['diff']=sel_year_dt['value'].sub( # 값 차이 계산
        before_year_dt['value'], fill_value=0) # 이전 연도 데이터 없을 시 0
    sel_year_dt['diff_abs']=abs(sel_year_dt['diff']) # 차이 절대값
    return pd.concat([ # 필요열만 추가
        sel_year_dt['city'],
        sel_year_dt['value'],
        sel_year_dt['diff'],
        sel_year_dt['diff_abs']
    ], axis=1).sort_values(by='diff', ascending=False) # 차이 큰 순서대로 정렬

dt_diff_sorted=cal_presale_diff(dt,sel_year,sel_category) # 차이존재, 정렬된 데이터 프레임 생성

dt_greater_10 = dt_diff_sorted[dt_diff_sorted['diff']>10] # 차이값 10 초과
dt_less_10 = dt_diff_sorted[dt_diff_sorted['diff']<-10] # 차이값 -10 미만

great_10=int((len(dt_greater_10)/dt['city'].nunique())*100) # 10 초과 도시 / 전체 도시 * 100
less_10=int((len(dt_less_10)/dt['city'].nunique())*100) # -10 미만 도시 / 전체 도시 * 100

# 도넛 그래프 설정
def make_donut(input_response,input_text,input_color):
    if input_color=='blue': # 색 정의
        chart_color=['#29b5e8','#155F7A']
    if input_color=='green':
        chart_color=['#27AE60','#12783D']
    if input_color=='orange':
        chart_color=['#F39C12','#875A12']
    if input_color=='red':
        chart_color=['#E74C3C','#781F16']

    source=pd.DataFrame({ # 도넛
        'Topic':['',input_text], # 레이블 생성
        '% value':[100-input_response,input_response] # 비율
    })
    source_bg=pd.DataFrame({ # 배경도넛
        'Topic':['',input_text],
        '% value':[100,0]
    })

    plot=alt.Chart(source).mark_arc(innerRadius=45,cornerRadius=25).encode( # 실제 도넛 플롯 생성
        theta='% value', # 각도비율
        color=alt.Color('Topic:N', # 색상매핑:범주
                        scale=alt.Scale(
                            domain=[input_text,''], # 도메인
                            range=chart_color), # 색상
                        legend=None), # 범례제거
    ).properties(width=130,height=130) # 차트 크기

    text=plot.mark_text(align='center',color='#29b5e8',font='Helvetica',fontSize=34, # 도넛 중앙 텍스트 설정
                        fontWeight=500,fontStyle='italic'
                       ).encode(text=alt.value(f'{input_response} %')) # 내용
    plot_bg=alt.Chart(source_bg).mark_arc(innerRadius=45,cornerRadius=25).encode( # 베경 도넛 플롯 생성
        theta='% value',
        color=alt.Color('Topic:N',
                        scale=alt.Scale(
                            domain=[input_text,''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130,height=130)
    return plot_bg+plot+text # 최종 차트 반환


## layout 설정
col=st.columns((1,5,2),gap='medium') # 1:5:2

with col[0]:
    # 텍스트박스
    st.markdown('#### 최대증감도시')
    dt_diff_sorted=cal_presale_diff(dt,sel_year,sel_category)

    if sel_year > 2015: # 가장 마지막인 2015년은 이전 데이터 없으므로
        first_state_name = dt_diff_sorted.city.iloc[0] # 도시 이름
        first_state_value = round(dt_diff_sorted['value'].iloc[0],2) # 값 소수점 둘째자리까지
        first_state_delta = round(dt_diff_sorted['diff'].iloc[0],2) # 차이 소수점 둘째자리까지
        st.metric(label=first_state_name, value=first_state_value, delta=first_state_delta)
    else: # 없음처리
        first_state_name = '-'
        first_state_value = '-'
        first_state_delta = ''
        st.metric(label=first_state_name, value=first_state_value, delta=first_state_delta)

    if sel_year > 2015:
        last_state_name = dt_diff_sorted.city.iloc[-1]
        last_state_value = round(dt_diff_sorted['value'].iloc[-1],2)
        last_state_delta = round(dt_diff_sorted['diff'].iloc[-1],2)
        st.metric(label=last_state_name, value=last_state_value, delta=last_state_delta)   
    else:
        last_state_name = '-'
        last_state_value = '-'
        last_state_delta = ''
        st.metric(label=last_state_name, value=last_state_value, delta=last_state_delta)
    st.write("")

    # 도넛차트
    st.markdown('#### 10%p 이상 변동비')
    if sel_year > 2015:
        great_10=int((len(dt_greater_10)/dt['city'].nunique())*100) # 10 초과 도시 / 전체 도시 * 100
        less_10=int((len(dt_less_10)/dt['city'].nunique())*100) # -10 미만 도시 / 전체 도시 * 100
    else:
        great_10=0
        less_10=0

    donut_greater=make_donut(great_10,'10%p증가 비율','green') # 도넛차트 그리기
    donut_less=make_donut(less_10,'10%p감소 비율','red')

    st.write('전체도시 중 증가비')
    st.altair_chart(donut_greater)
    st.write('전체도시 중 감소비')
    st.altair_chart(donut_less)

with col[1]:
    # choropleth 시각화
    st.markdown('#### 지역별 시각화')
    st.plotly_chart(choropleth,use_container_width=True)
    
    # heatmap
    st.write('')
    st.write('초기분양률')
    st.altair_chart(heatmap_pre,use_container_width=True)
    st.write('공급부담지표')
    st.altair_chart(heatmap_ss,use_container_width=True)

with col[2]:
    # 상위도시
    dt_year_target_sorted = dt_year_target.sort_values(by='value', ascending=False) # 정렬

    st.markdown('#### 상위도시')

    st.dataframe(dt_year_target_sorted,
                 column_order=('city','value'),
                 hide_index=True,
                 width=400,
                 column_config={
                     'city':st.column_config.TextColumn(
                         '도시',
                     ),
                     'value':st.column_config.ProgressColumn(
                         '값',
                         format='%.2f',
                         min_value=0,
                         max_value=max(dt_year_target['value'])
                     )}
                )
    
    # 참고
    with st.expander('About', expanded=True):
        st.write('''
                 - Data1 : [국토교통부, 지역별 민간아파트 평균 초기분양률](<https://kosis.kr/statHtml/statHtml.do?orgId=390&tblId=DT_39002_04&vw_cd=MT_ZTITLE&list_id=I2_3&scrId=&seqNo=&lang_mode=ko&obj_var_id=&itm_id=&conn_path=MT_ZTITLE&path=%252FstatisticsList%252FstatisticsListIndex.do>)
                 - Data2 : [국토교통부, 민간아파트 미분양현황](<https://kosis.kr/statHtml/statHtml.do?orgId=390&tblId=DT_39002_04&vw_cd=MT_ZTITLE&list_id=I2_3&scrId=&seqNo=&lang_mode=ko&obj_var_id=&itm_id=&conn_path=MT_ZTITLE&path=%252FstatisticsList%252FstatisticsListIndex.do>)
                 - 공급부담지표 = log(미분양수)/초기분양수 * 100
                 - 공급부담지표 증가 시, 과잉공급 가능성 증가
                 - 10%p 이상 변동비 = 10%p 이상 증가,감소 도시수 / 전체 도시수
                 ''')