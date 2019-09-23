import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
from datetime import datetime as dt
from dash_auth import BasicAuth

username_passwords = [['admin','lucafaloni']]

# Load and process data

def month_year(col):
    m = col[0]; y = col[1]
    return m + ' ' + str(y)   

df = pd.read_csv('data.csv')
df.fillna('__N/A__', inplace=True)

df['Date'] = pd.to_datetime(df['day'])
df['WeekofYear'] = df['Date'].apply(lambda d: d.weekofyear)
df['Year'] = df['Date'].apply(lambda d: d.year)
df['Month_Name'] = df['Date'].apply(lambda d: d.month_name())
df['Month_Year'] = df[['Month_Name','Year']].apply(month_year,axis=1)
df['color'] = df['product_title'].apply(lambda p: p.split()[0])
df['Dummy'] = 1

gdf_month = df.groupby(by='Month_Year').sum().reset_index()
gdf_month['Month_Start'] = pd.to_datetime(gdf_month['Month_Year'])
gdf_month.sort_values(by='Month_Start',inplace=True)

def gdf_month_filter(item,feature):
    global df
    gdf_month = df[df[feature]==item].groupby(by='Month_Year').sum().reset_index()
    gdf_month['Month_Start'] = pd.to_datetime(gdf_month['Month_Year'])
    gdf_month.sort_values(by='Month_Start',inplace=True)
    return gdf_month

def gdf_wd_filter(item,feature,wd,sd,ed):
    global df
    gdf_wd = df[(df[feature]==item) & (df['Date']>=sd) & (df['Date']<=ed)].groupby(by=wd).sum().reset_index()
    gdf_wd.sort_values(by=wd,inplace=True)
    return gdf_wd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Build Dashboard

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

auth = BasicAuth(app,username_passwords)

# Defining Dash Core Components

graph_bymonth = dcc.Graph(
    id='graph_bymonth',
    hoverData={'points': [{'x': 'January 2019'}]}
    )

graph_byweekorday = dcc.Graph(id='graph_byweekorday')

pie_bymonth = dcc.Graph(id='pie_bymonth')

byweekorday = dcc.Dropdown(id='byweekorday', options=[
    {'label':'Week','value':'Week'},
    {'label':'Day','value':'Day'}],
    value='Week')

itemlist = dcc.Dropdown(id='itemlist',multi=True)

value_dict={'total_sales':'Total Sales', 'net_quantity':'Net Quantity'}

feature_dict={'product_type':'Product',
    'variant_title':'Size',
    'color':'Color',
    'shipping_country':'Shipping Country',
    'shipping_city':'Shipping City',
    'shipping_region':'Shipping Region'
}

featurelist = dcc.Dropdown(id='featurelist',options=[
    {'label':feature_dict[k],'value':k} for k in feature_dict
], value='product_type')

value_op = dcc.RadioItems(id='value_op',
    options=[
        {'label':'Total Sales','value':'total_sales'},
        {'label':'Net Quantity','value':'net_quantity'}
    ], value='net_quantity',
    labelStyle={'display': 'inline-block'}
)

date_range = dcc.DatePickerRange(
        id='date_range',
        min_date_allowed=df['Date'].min(),
        max_date_allowed=df['Date'].max(),
        start_date=df['Date'].min(),
        end_date=df['Date'].max(),
        display_format='DD/MM/YYYY',
        clearable=False
    )
# Defining Dash Layout

app.layout = html.Div(children=[
    html.H1(children='Luca Faloni Dashboard',style={'display':'inline-block'}),
    featurelist,
    itemlist,
    html.Div(value_op),
    html.Div(children=[
        graph_bymonth
    ], style={'width':'70%','display':'inline-block'}),
    html.Div(children=[
        pie_bymonth
    ], style={'display':'inline-block','float':'right'}),
    html.Div(),
    html.Div(children=[date_range],style={'display':'inline-block','width':'15%'}),
    html.Div(children=[byweekorday],style={'display':'inline-block','width':'15%'}),
    html.Div(children='Please hover on the main plot to update the Pie Chart data',style={'display':'inline-block','float':'right'}),
    graph_byweekorday
    ])

# Linking Interactive Components

@app.callback(
    Output(component_id='itemlist',component_property='options'),
    [Input(component_id='featurelist',component_property='value')]
)
def set_itemlist_options(feature):
    return [{'label': i, 'value': i} for i in df[feature].unique()]

@app.callback(
    Output(component_id='itemlist',component_property='value'),
    [Input(component_id='featurelist',component_property='value')]
)
def set_itemlist_value(feature):
    return df[feature].unique()

@app.callback(
    Output(component_id='graph_bymonth',component_property='figure'),
    [Input(component_id='itemlist',component_property='value'),
    Input(component_id='featurelist',component_property='value'),
    Input(component_id='value_op', component_property='value')]
)
def update_bymonth(items,feature,value_op):
    global value_dict
    trace=[{'x': gdf_month['Month_Year'], 'y': gdf_month[value_op], 'type':'line','name':'All'}]
    datadict_bymonth_extend = [{'x': gdf_month_filter(item,feature)['Month_Year'], 'y': gdf_month_filter(item,feature)[value_op], 
                'type': 'line', 'name': item} for item in items]
    trace.extend(datadict_bymonth_extend)
    return {
        'data':trace,
        'layout': {
            'title': value_dict[value_op] + ' by Month',
            'barmode': 'stack',
            'hovermode': 'closest'
        }
    }

@app.callback(
    Output(component_id='graph_byweekorday',component_property='figure'),
    [Input(component_id='itemlist',component_property='value'),
    Input(component_id='featurelist',component_property='value'),
    Input(component_id='value_op', component_property='value'),
    Input(component_id='date_range', component_property='start_date'),
    Input(component_id='date_range', component_property='end_date'),
    Input(component_id='byweekorday',component_property='value')]
)
def update_byweekorday(items,feature,value_op,start_date,end_date,weekorday):
    global value_dict, df
    xis = 'WeekofYear' if weekorday =='Week' else 'Date'
    trace=[{
        'x': gdf_wd_filter(1,'Dummy',xis,start_date,end_date)[xis], 
        'y': gdf_wd_filter(1,'Dummy',xis,start_date,end_date)[value_op], 
        'type':'line','name':'All'
    }]
    datadict_bywd_extend = [{
        'x': gdf_wd_filter(item,feature,xis,start_date,end_date)[xis], 
        'y': gdf_wd_filter(item,feature,xis,start_date,end_date)[value_op], 
        'type': 'lines+marker', 
        'name': item} for item in items]
    trace.extend(datadict_bywd_extend)
    return {
        'data':trace,
        'layout': {
            'title': value_dict[value_op] + ' by ' + weekorday,
            'barmode': 'stack',
            'hovermode': 'closest'
        }
    }

@app.callback(
    Output(component_id='pie_bymonth',component_property='figure'),
    [Input(component_id='itemlist',component_property='value'),
    Input(component_id='featurelist',component_property='value'),
    Input(component_id='value_op', component_property='value'),
    Input(component_id='graph_bymonth',component_property='hoverData')]
)
def update_bymonth(items,feature,value_op,month):
    global value_dict, feature_dict, df
    pivotdf = df.pivot_table(values=value_op,index=feature,columns='Month_Year',aggfunc='sum')
    pivotdf.fillna(0,inplace=True)
    # trace_all = [{'labels':['All'], 'values':[0], 'type':'pie', 'hole':0.4}]
    trace = [{'labels':pivotdf.index, 'values':pivotdf[month['points'][0]['x']].get_values(), 'type':'pie', 'hole':0.4}] # [{'x': gdf_month['Month_Year'], 'y': gdf_month[value_op], 'type':'line','name':'All'}]
    return {
        'data':trace,
        'layout': {
            'title': value_dict[value_op]+' Distribution by '+feature_dict[feature]+' for '+month['points'][0]['x'],
            'hovermode': 'closest'
        }
    }


if __name__ == '__main__':
    app.run_server(debug=True)