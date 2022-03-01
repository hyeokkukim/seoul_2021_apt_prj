#패키지 및 데이터 import
import json
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os
from plotly.subplots import make_subplots
import requests

apt21 = pd.read_csv('https://raw.githubusercontent.com/hyeokkukim/seoul_2021_apt_prj/main/seoul_apt_price_2021.csv',index_col=0)

df1 = pd.DataFrame(apt21.groupby('법정동')['평당거래_만원'].mean())
df1.columns = ['거래가격']
count = apt21.groupby('법정동')['평당거래_만원'].count().tolist()
df1['거래횟수'] = count
df1 = df1.reset_index()

new_geo = requests.get('https://raw.githubusercontent.com/hyeokkukim/seoul_2021_apt_prj/main/seoul_beobjeongdong.geojson').json()


#기본 설정 불러오기
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div(children=[
    html.H1(children='Seoul housing project',
        style={
            'textAlign': 'left',
            'color': 'black'
        }),#제목

    html.Div(children='made by Hyeokku Kim @University of Seoul', style={
        'textAlign': 'left',
        'color': 'black'
    })
    ]),
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                ['거래횟수','거래가격'],
                '거래횟수',
                placeholder='Select..',
                id = 'crossfilter-left-column')],
                style={'width':'49%','display':'inline-block'}),

        html.Div([
            dcc.Dropdown(
                apt21['법정구'].unique(),
                '강남구',
                placeholder='Select..',
                id = 'crossfilter-right-column')],
                style={'width':'49%','float':'right','display':'inline-block'})
    ]),
    html.Div([
        dcc.Graph(id='crossfilter-left-graphic')],
        style={'width':'49%','display':'inline-block'}),

    html.Div([
        dcc.Graph(id='crossfilter-right-graphic')],
        style={'width':'49%','display':'inline-block'})
])
'''
    html.Div(dcc.Slider(1990,2021,value=1990,id='year--slider',
                marks={str(year): str(year) for year in years}),
                style={'width':'49%','padding':'0px 20px 20px 20px'})
])'''


@app.callback(
    Output('crossfilter-left-graphic', 'figure'),
    Input('crossfilter-left-column', 'value'))
def update_graph(left_value):

    fig = px.choropleth_mapbox(data_frame = df1, #데이터셋
                           geojson=new_geo, #geojson 파일
                           locations='법정동', #데이터에서 매칭시킬 컬럼 지정
                           color=left_value, #volumne 컬럼
                           color_continuous_scale='Plasma', #color scale
                           featureidkey = 'properties.EMD_NM', #geojson에서 매칭시킬 컬럼 지정
                           mapbox_style='carto-positron',
                           zoom=10,
                           center = {"lat": 37.563383, "lon": 126.996039}, #중심점 = 서울
                           opacity=0.5,
                          )

    fig.update_layout(showlegend = False,
        title = dict(text='서울시 법정동별 2021 아파트 '+ left_value,
            font = dict(size=13,color='black'),
            x = 0.08, y = 0.958),     width=750,height=550)
    return fig

@app.callback(
    Output('crossfilter-right-graphic','figure'),
    Input('crossfilter-right-column','value')
)
def update_graph(gu_value):

    df = apt21[apt21['법정구'] == gu_value]

    df = pd.DataFrame(df.groupby('단지명')['평당거래_만원'].mean()).reset_index()

    count = pd.DataFrame(apt21.groupby('단지명')['평당거래_만원'].count()).reset_index()
    df['count'] = count['평당거래_만원']

    df=df.sort_values(by='평당거래_만원',ascending=False)
    df = df.head(50)
    

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(name = '거래금액', x = df['단지명'], y=df['평당거래_만원'], width=0.4,marker_color = '#ffb703'),secondary_y=False)
    fig.add_trace(go.Scatter(name='거래건수',x=df['단지명'],y=df['count'],mode='markers',marker=dict(size=4,color='#262254')),secondary_y=True) 


    fig.update_layout(showlegend = True,
        title = dict(text='2021년 '+str(gu_value)+' 아파트별 평당평균거래가격 상위 50',
            font = dict(size=13,color='black'),
            x = 0.08, y = 0.89),
        legend = dict(orientation = 'h', x = 0, y = 1.036, font = dict(size = 8, color = 'black')),
        xaxis = dict(
            title = '단지명',
            titlefont = dict(
                size = 10,
                color = 'black'),
            tickmode = 'linear', #x축 라벨 모두 보이기
            showline = True,
            showgrid = True,
            linecolor = 'black',
            linewidth = 0.8,
            ticks = 'outside',
            tickfont = dict(
                size = 8,
                color = 'black')),
        width=750,height=550,
        plot_bgcolor = 'white')


    fig.update_yaxes(title_text='평당평균거래금액(만원)',titlefont=dict(size = 10,color = 'black'),
            showline = True, showgrid = True, linecolor = 'black', linewidth = 0.8,
            ticks = 'outside', tickfont = dict(size = 8, color = 'black'),secondary_y=False)

    fig.update_yaxes(title_text='거래건수',titlefont=dict(size = 10,color = 'black'),
            showline = True, showgrid = True, linecolor = 'black', linewidth = 0.8,
            ticks = 'outside', tickfont = dict(size = 8, color = 'black'),secondary_y=True)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

'''
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
import json


app = Dash(__name__)


# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

df = pd.read_csv('/Users/hyeokkukim/Library/CloudStorage/OneDrive-UOS/7.서울시민의_공간향유_변화/7-2.Coding/220223_법정구별_향유공간.csv',index_col=0)
with open('/Users/hyeokkukim/OneDrive - UOS/0.Python/seoul_beobjeongdong.geojson','r') as f:
    new_geo = json.load(f)

fig = px.choropleth_mapbox(data_frame = df, #데이터셋
                           geojson=new_geo, #geojson 파일
                           locations='geo_code', #데이터에서 매칭시킬 컬럼 지정
                           color='2021', #volumne 컬럼
                           color_continuous_scale='Plasma', #color scale
                           featureidkey = 'properties.EMD_CD', #geojson에서 매칭시킬 컬럼 지정
                           mapbox_style='carto-positron',
                           zoom=10,
                           center = {"lat": 37.563383, "lon": 126.996039}, #중심점 = 서울
                           opacity=0.5
                          )

app.layout = html.Div([
    html.Div(style={'backgroundColor': 'white'}, children=[
    html.H1(
        children='title, 제목',
        style={
            'textAlign': 'center',
            'color': 'red'
        }),#제목

    html.Div(children='subtitle, 부제목', style={
        'textAlign': 'center',
        'color': 'green'
    }),#소제목

    dcc.Graph(
        id='example-graph-2',
        figure=fig
    )#그래프
    ]),

    html.Div(children=[
        html.Label('Slider'),
        dcc.Slider(
            min=1990,
            max=2021,
            value=1)])])

if __name__ == '__main__':
    app.run_server(debug=True)

    '''
