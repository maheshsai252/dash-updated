import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.graph_objs as go1
from dash.dependencies import Input, Output
import pandas as pd

baseURL = "//Users//maheshsai//Downloads//novel-corona-virus-2019-dataset-2/"
world_coordinates = pd.read_csv('//Users//maheshsai//Desktop//world_coordinates.csv')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

tickFont = {'size':12, 'color':"rgb(30,30,30)", 'family':"Courier New, monospace"}

def loadData(fileName, columnName):
    data = pd.read_csv(baseURL + fileName).drop('SNo',axis=1)
    data['Province/State'].fillna('<all>', inplace=True)
    #data[columnName].fillna(0, inplace=True)
    data['ObservationDate'] = pd.to_datetime(data['ObservationDate'], errors='coerce')
    data['dateStr'] = data['ObservationDate'].dt.strftime('%d/%m/%Y')
    return data

allData = loadData("covid_19_data.csv", "CumConfirmed")

India_coord = pd.read_csv('//Users//maheshsai//Downloads//coronavirus-cases-in-india//Indian Coordinates.csv')
   # .merge(loadData("time_series_covid_19_deaths.csv", "CumDeaths")) \
    #.merge(loadData("time_series_covid_19_recovered.csv", "CumRecovered"))
ind_df=pd.read_csv("//Users//maheshsai//Downloads//coronavirus-cases-in-india//Covid cases in India.csv")
ind_df['Total cases'] = ind_df['Total Confirmed cases (Indian National)'] + ind_df['Total Confirmed cases ( Foreign National )']
ind_df['Active cases'] = ind_df['Total cases'] - (ind_df['Cured/Discharged/Migrated'] + ind_df['Deaths'])
countries = allData['Country/Region'].unique()
countries.sort()
da=allData['dateStr'].unique()
    #da=allData['dateStr'].unique()
da1=[]
da2=[]
da3=[]
max_value = ind_df['Deaths'].max()
new_d = ind_df[['Name of State / UT','Cured/Discharged/Migrated','Deaths','Total cases','Active cases']]
for i in da:
    if(i[3:5]=='01'):
        da1.append(i)
    elif (i[3:5]=='02'):
        da2.append(i)
    else:
        da3.append(i)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title='Coronavirus'
app.layout = html.Div(
    style={ 'font-family':"Courier New, monospace" },
    children=[
    html.H1('Dashboard of  Coronavirus (COVID-19)',style={'color': '#a8a222'}),
    html.Div(className="row", children=[
        html.Div(className="four columns", children=[
            html.H5('Country',style={'color': '#296665'}),
            dcc.Dropdown(
                id='country',
                options=[{'label':c, 'value':c} for c in countries],
                value='Italy'
            )
        ]),
        html.Div(className="four columns", children=[
            html.H5('State / Province',style={'color': '#296665'}),
            dcc.Dropdown(
                id='state'
            )
        ]),
        html.Div(className="four columns", children=[
            html.H5('Selected Metrics',style={'color': '#296665'}),
            dcc.Checklist(
                id='metrics',
                options=[{'label':m, 'value':m} for m in ['Confirmed', 'Deaths', 'Recovered']],
                value=['Confirmed', 'Deaths']
            )
        ])
    ]),
    dcc.Graph(
        id="plot_new_metrics",
        config={ 'displayModeBar': False }
    ),
    html.H3('State wise plot',style={'color':'#a8a222'}),

    dcc.Graph(
        id="plot_new_states",
        config={ 'displayModeBar': False }
    ),
    html.H3('Coronavirus (COVID-19) in India',style={'color':'#a8a222'}),

    dcc.Graph(id = 'plot_india'),
    html.H3('Coronavirus (COVID-19) representation in World map',style={'color':'#a8a222'}),

    dcc.Graph(id = 'countryMap'),

    #html.Div(html.H5('@ Mahesh Sai',style={'color':'#583b69'}))
    dcc.Slider(
        id='my-slider',
            min=0,
            max=10,
            step=None,
            marks={
            0: 'Jan ',
            5: 'Feb',
            10: 'March',
            },
            value=5
            )
    ,
    dcc.Graph(id='indiamap'),
    html.Div(id='slider-output-container'),
    html.H3('State wise chart of Coronavirus (COVID-19) in India',style={'color':'#a8a222'}),
    dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in new_d.columns],
            data=new_d.to_dict("rows"),
            style_data={
            'border':'1px solid black',
            'font-size':'1.2em'
            },
            style_data_conditional=[
            {
            'if': {
            'column_id':'Deaths',
            'filter_query':'{Deaths} > 0'
            },
            'backgroundColor':'red'
            },
            {
            'if': {
            'column_id':'Active cases',
            'filter_query':'{Active cases} > 10'
            },
            'backgroundColor':'orange'
            },],
            style_cell={'width': '300px',
            'height': '60px',
            'textAlign': 'left',
            'border' : '1px solid grey'},
            style_table={
            'height':'600px',
            'width':'900px',
            'margin-left':'200px',
            'margin right':'40 px'
            },
            filter_action="native",
            sort_action="custom",
            sort_mode = "multi",
            column_selectable="single",
            sort_by=[])



])

@app.callback(
    [Output('state', 'options'), Output('state', 'value')],
    [Input('country', 'value')]
)
def update_states(country):
    states = list(allData.loc[allData['Country/Region'] == country]['Province/State'].unique())
    states.insert(0, '<all>')
    states.sort()
    state_options = [{'label':s, 'value':s} for s in states]
    state_value = state_options[0]['value']
    return state_options, state_value

def nonreactive_data(country, state):
    data = allData.loc[allData['Country/Region'] == country].drop('Country/Region', axis=1)

    if state == '<all>':
        data = data.drop('Province/State', axis=1)
    else:
        data = data.loc[data['Province/State'] == state]

    return data

def nonreactive_data2(country, state):
    data = allData.loc[allData['Country/Region'] == country].drop('Country/Region', axis=1)

    return data
def barchart(data, metrics, prefix="", yaxisTitle=""):
    figure = go.Figure(data=[
        go.Line(
            name=metric, x=data.ObservationDate, y=data[metric],
            marker_line_color='rgb(0,0,0)', marker_line_width=1,
            marker_color={ 'Deaths':'rgb(200,30,98)', 'Recovered':'rgb(30,200,30)', 'Confirmed':'rgb(100,200,240)'}[metric]
        ) for metric in metrics
    ])
    figure.update_layout(
              barmode='group', legend=dict(x=.05, y=0.95, font={'size':15}, bgcolor='rgba(240,200,240,0.5)'),
              plot_bgcolor='#FFFFFF', font=tickFont) \
          .update_xaxes(
              title="", tickangle=-90, type='category', showgrid=True, gridcolor='#DDDDD0',
              tickfont=tickFont, ticktext=data.dateStr, tickvals=data.ObservationDate) \
          .update_yaxes(
              title=yaxisTitle, showgrid=True, gridcolor='#DDDDDD')
    return figure

def barchartstate(data, metrics, prefix="", yaxisTitle=""):
    figure = go.Figure(data=[
        go.Bar(
            name=metric, x=data['Province/State'], y=data[metric],
            marker_line_color='rgb(0,0,0)', marker_line_width=1,
            marker_color={ 'Deaths':'rgb(200,30,98)', 'Recovered':'rgb(30,200,30)', 'Confirmed':'rgb(100,200,240)'}[metric]
        ) for metric in metrics
    ])
    figure.update_layout(
              barmode='group', legend=dict(x=.05, y=0.95, font={'size':15}, bgcolor='rgba(240,200,240,0.5)'),
              plot_bgcolor='#FFFFFF', font=tickFont) \
          .update_xaxes(
              title="", tickangle=-90, type='category', showgrid=True, gridcolor='#DDDDD0',
              tickfont=tickFont, ticktext=data['Province/State'], tickvals=data['Province/State']) \
          .update_yaxes(
              title=yaxisTitle, showgrid=True, gridcolor='#DDDDDD')
    return figure
def barchartindia():


	ds=ind_df.sort_values('Active cases',ascending=True)
	ds=ds[['Active cases','Name of State / UT']]
	figure = go.Figure(data=[
		go.Bar(y=ds['Active cases'], x = ds['Name of State / UT'])])
	figure.update_layout(
              barmode='group', legend=dict(x=.05, y=0.95, font={'size':15}, bgcolor='rgba(240,200,240,0.5)'),
              plot_bgcolor='#FFFFFF', font=tickFont) \
          .update_xaxes(
              title="", tickangle=-90, type='category', showgrid=True, gridcolor='#DDDDD0',
              tickfont=tickFont, ticktext=ds['Name of State / UT'], tickvals=ds['Name of State / UT']) \
          .update_yaxes(
              title="active cases", showgrid=True, gridcolor='#DDDDDD')

	return figure
@app.callback(
    Output('plot_new_metrics', 'figure'),
    [Input('country', 'value'), Input('state', 'value'), Input('metrics', 'value')]
)
def update_plot_new_metrics(country, state, metrics):
    data = nonreactive_data(country, state)
    return barchart(data, metrics, prefix="New", yaxisTitle="cumulaive Cases ")
@app.callback(
    Output('plot_india', 'figure'),
    [Input('country', 'value'), Input('state', 'value'), Input('metrics', 'value')]
)
def update_plot_india_metrics(country, state, metrics):
    return barchartindia()

def makeScatterMap(value):
	#allData.rename(columns = {'Country/Region':'Country'}, inplace = True)
    if(value==0):
        allData1=allData[allData['dateStr'].isin(da1)]
    elif(value==5):
        allData1=allData[allData['dateStr'].isin(da2)]
    else:
        allData1=allData[allData['dateStr'].isin(da3)]
    allData1['Country'] = allData1['Country/Region']
    world_data = pd.merge(world_coordinates,allData1,on='Country')
    world_data['Confirmed']=world_data['Confirmed'].astype(str)
    world_data['Deaths']=world_data['Deaths'].astype(str)
	#world_data['Recovered']=world_data['Recovered'].astype(str)
    scl = [0,"rgb(150,0,0)"],[0.125,"rgb(100, 0, 0)"],[0.25,"rgb(0, 25, 0)"],\
    [0.375,"rgb(0, 152, 0)"],[0.5,"rgb(44, 255, 0)"],[0.625,"rgb(151, 0, 0)"],\
    [0.75,"rgb(255, 234, 0)"],[0.875,"rgb(255, 111, 0)"],[1,"rgb(255, 0, 0)"]
    data = [
    go1.Scattergeo(
		lat = world_data['latitude'],
		lon=world_data['longitude'],
		text=world_data['Country']+'\n'+'Confirmed : '+(world_data['Confirmed'])+'\n'+'Deaths : '+(world_data['Deaths']),
		marker=dict(
			color=(world_data['Recovered']%100)*0.01,
			size=7,

			opacity=0.7))

	]
    fig=go1.Figure(data=data)
    fig.update_layout(title='World map',height=700)
    return fig
def makeScatterMapindia(value):
	#allData.rename(columns = {'Country/Region':'Country'}, inplace = True)
	#allData['Country'] = allData['Country/Region']
	data1 = pd.merge(ind_df,India_coord,on='Name of State / UT')
	data1['Total cases']=data1['Total cases'].astype(str)
	data1['Deaths']=data1['Deaths'].astype(str)
	#world_data['Recovered']=world_data['Recovered'].astype(str)
	scl = [0,"rgb(150,0,0)"],[0.125,"rgb(100, 0, 0)"],[0.25,"rgb(0, 25, 0)"],\
	[0.375,"rgb(0, 152, 0)"],[0.5,"rgb(44, 255, 0)"],[0.625,"rgb(151, 0, 0)"],\
	[0.75,"rgb(255, 234, 0)"],[0.875,"rgb(255, 111, 0)"],[1,"rgb(255, 0, 0)"]
	data = [
	go1.Scattergeo(
		lat = data1['Latitude'],
		lon=data1['Longitude'],
		text=data1['Name of State / UT']+'\n'+'Confirmed : '+(data1['Total cases'])+'\n'+'Deaths : '+(data1['Deaths']),
		marker=dict(
			color=(data1['Active cases']%100)*0.01,
			size=7,

			opacity=0.7))

	]
	fig=go1.Figure(data=data)
	fig.update_layout(title='World map-INDIA',height=700,mapbox_center = {"lat": 60.0902, "lon": 40.7129})
	return fig
@app.callback(
    Output('countryMap', 'figure'),
    [Input('my-slider', 'value')]
)
def update_plot_world_metrics(value):
    return makeScatterMap(value)
@app.callback(
    Output('indiamap', 'figure'),
    [Input('my-slider', 'value')]
)
def update_plot_indiamap_metrics(value):
    return makeScatterMapindia(value)

@app.callback(
    Output('plot_new_states', 'figure'),
    [Input('country', 'value'), Input('state', 'value'), Input('metrics', 'value')]
)
def update_plot_new_states(country, state, metrics):
    data = nonreactive_data2(country, state)
    return barchartstate(data, metrics, prefix="New", yaxisTitle="cumulaive Cases ")
@app.callback(
    Output('table', 'data'),
    [Input('table', 'sort_by')]
)
def update_output(sort_by):
    print(sort_by)
    df=new_d
    if len(sort_by) :
        dff = df.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
            col['direction'] == 'asc'
            for col in sort_by],
            inplace=False
            )
    else:
        dff = df
    return dff.to_dict('records')



server = app.server
@server.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(server.root_path, 'static'),
                                     'favicon.ico')

if __name__ == '__main__':
    app.run_server(debug=True)
