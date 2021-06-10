import dash_html_components as html
import dash_core_components as dcc
#import dash_bootstrap_components as dbc

import dash


import plotly.graph_objs as go 

from prophet.diagnostics import performance_metrics


from dash.dependencies import Input, Output, State
import dash_table as dt

import pandas as pd

import json
from datetime import datetime



import base64
import io
from dash.exceptions import PreventUpdate
import functions_app as f




app = dash.Dash(__name__, 
                title='Probabilistic Forecasting',
                #external_stylesheets=[dbc.themes.FLATLY]
                )

server = app.server

app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

all_options = {
    #'percentiles': [0.05, 2.5, 5, 15, 25, 50, 75, 90, 95, 97.5, 99.95 ],
    'metrics': ['mse', 'rmse', 'mae', 'mape', 'coverage']
}





app.layout = html.Div([
    
    html.H1("Time Series Quantile Forecasting",
            style={
                'textAlign': 'center', 
                'color': 'blue',
                'family': 'verdana',
                'size': '50%'
                }),
    
    html.Hr(),
    
    dcc.Tabs([
        dcc.Tab(label='Homepage', children=[
    
    
    
    
    html.H3("1. Input data",
            style = {'color': 'blue'}),
    
    html.Div([
                
        html.H5("Upload CSV/Excel File"),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select CSV/Excel File')
                ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'display': 'inline-block'
                },
            multiple=False)
        ],
        style={'width': '60%', 'float': 'center', 'display': 'inline-block'
                   }),


    html.Br(),
    
    html.H5("Select the period to forecast"),
        html.P("Start date is the day after last observation."),
        
        dcc.DatePickerSingle(
            id='endate',
            #min_date_allowed=date(2016, 1, 2),
            display_format='MM/DD/YYYY',
            #initial_visible_month=date(2017, 12, 31),
            placeholder="End Date"),
        html.Br(),
    

    
    html.Div([
        html.H5("Select Date Column"),
        
        dcc.Dropdown(id='dropdown_table_filterDate',
                     multi = False,
                     placeholder='Select Date Variable'),
        
        html.Br(),
        html.H5("Select Response Column"),
        dcc.Dropdown(id='dropdown_table_filterResponse',
                     multi = False,
                     placeholder='Select Response Variable')],
        
        style={'width': '30%', 'float': 'center', 'display': 'inline-block'
               }),
    
    html.Br(),
             
    
    html.H5("Select parameters for cross-validation"),
    
    
    dcc.Input(
                id="initial",
                type="number",
                placeholder="Initial (days)",
                min=10,
                #value = 5000,
                debounce=True),
    dcc.Input(
                id="period",
                type="number",
                placeholder="Period (days)",
                min=10,
                #value = 180,
                debounce=True),
    dcc.Input(
                id="horizon",
                type="number",
                placeholder="Horizon (days)",
                min=10,
                #value = 365,
                debounce=True),

    
    html.Div(id='result-intermedio', style={'display': 'none'}),
    
    html.Br(),
    html.Br(),
    html.Button(
        id='propagate-button',
        n_clicks=0,
        children="Let's make our predictions!"),


#    html.Br(),
#    html.H5("Updated Table"),
#    html.Div(
        
#        dt.DataTable(
#        id='table',
#        columns=[],
#        data=[],
#        page_size=15,
#        style_cell={
#        "textAlign": 'left',
#        },
#        style_header=dict(backgroundColor="paleturquoise"),
#        style_data=dict(backgroundColor="lavender"),
#        style_table={'overflowX': 'scroll'}
#        )),
    
    html.Br(),
  
        

    html.Hr(),
    
    html.H3("2. Results",
            style = {'color': 'blue'}),
    html.H4("Forecast plot",
            style = {'color': 'blue'}),
    html.P("The mean estimate and prediction intervals are computed from 1000 samples drawn from the posterior predictive distribution."),
    html.P("A prediction interval gives a range of specified coverage probability under that distribution."),
    html.Div([
            html.Ul(children=[html.Li("The 95% prediction interval is defined by the 2.5% and 97.5% quantiles of the forecast distribution (if gaussian)."), 
                              html.Li("The 50% prediction interval is defined by the 25% and 75% quantiles of the forecast distribution (if gaussian).")])
        ]),
    
    dcc.Graph(id='plot'),
    
    html.Div(id='result-cv-intermedio', style={'display': 'none'}),
    
    html.Div(id='result-posteriorsamples-intermedio', style={'display': 'none'}),
    
    html.H4("Numerical results",
            style = {'color': 'blue'}),
    
     html.Div(
        
        dt.DataTable(
            id='predictions-table',
            columns=[],
            data=[],
            page_size=15,
            style_cell={
                "textAlign": 'left',
                },
            style_header=dict(backgroundColor="orange"),
            style_data=dict(backgroundColor="lavender"),
            export_format='xlsx',
            export_headers='display', 
            style_table={'overflowX': 'scroll'}
            )),

    html.Hr(),
    
    
    html.H3("3. Cross-Validation",
            style = {'color': 'blue'}),
    
    html.H5("Select performance metric to plot"),
    dcc.Dropdown(id='dropdown-metric',
        multi = False,
        options= [{'label': k, 'value': k} for k in all_options["metrics"]],
        value = "rmse",
        placeholder='Select performance metric to plot'),
     
    html.Br(),
    html.Button(
        id='cv-button',
        n_clicks=0,
        children="Let's check cross-validation!"),
    
    html.Br(),
    
    
    dcc.Graph(id='plot-cv'),
    
    html.H5("Cross validation performance metrics", 
            style = {'color': 'blue'}),
    
    html.Div(
        
        dt.DataTable(
        id='table-cv',
        columns=[],
        data=[],
        page_size=15,
        style_cell={
        "textAlign": 'left',
        },
        style_header=dict(backgroundColor="orange"),
        style_data=dict(backgroundColor="lavender"),
        export_format='xlsx',
        export_headers='display', 
        style_table={'overflowX': 'scroll'}
        )),
    
    html.Br(),


    
        
    html.Div(id='result-post-predic', style={'display': 'none'}),
    
    
    
    
    
    html.Hr(),
    
    html.Div([
        html.Span(["Carlos J Peña",
                  html.Br(),
                  "Jr. Biologist & Biostatistician", 
                  
                  html.Br(),
                  "Greater Bilbao, Basque Country - Spain"
                 
                  
                  ],
                  
                  style={'font-family': 'Calibri', 'font-size':'16px',
                         'color':'#31557F', 'text-align': 'center'}
                  ),
        html.Br(),
        html.Br(),
         
         
         html.A(
             html.Img(src="https://github.githubassets.com/images/modules/site/icons/footer/linkedin.svg", 
                     style={'width':'20px'}),
             href="https://www.linkedin.com/in/carljpena8/?viewAsMember=true"), 
                         
         html.A(
             html.Img(src="https://github.githubassets.com/images/modules/site/icons/footer/github-mark.svg", 
                      style={'width':'20 px'}),
             href="https://github.com/carlosjps")
        
                ],
        style = { 'text-align': 'center'}),
       
    
    html.Br()


]), 
        dcc.Tab(label='About', children=[
            html.H3("1. About this dashboard",
                    style = {'color': 'blue'}),
            
            html.Div([
            html.Ul(children=[html.Li('''This dashboard is the result of my modest attempt to create a 
                                      Dash app that produces univariate time series predictions in a user-friendly way.'''), 
                              html.Li('''It is intended to generate probabilistic forecasts of future observations 
                   by sampling from the predictive posterior distribution.''')])
        ]),
                               
            html.H3("2. Forecasting method", 
                    style = {'color': 'blue'}),
            dcc.Markdown('''The used forecasting framework is the *prophet* procedure 
                         developed by [Facebook](https://facebook.github.io/prophet/).
                         All of the specific details for this modeling technique can
                         be found at the [prophet documentation](https://facebook.github.io/prophet/)
                         and the paper [*Forecasting at scale*](https://peerj.com/preprints/3190/). 
                         \n I highly recommend reviewing this documentation to adapt the model 
                         to your data more appropriately by modifying the source code of this app.  
                         
                         '''),
                         
            html.H3("3. Input Data",
                    style = {'color': 'blue'}),
            dcc.Markdown(
                '''
                \n * The input data must be a CSV or Excel file containing 
                **at least two columns** with daily values of the variables of interest.
                These variables may be then selected from a dropdown menu to indicate which ones are 
                the *response* and *time*. \n * [Time series cross-validation](https://otexts.com/fpp3/tscv.html) 
                is used to diagnose the model. For this reason,
                it is necessary to enter the initial training period, the *period* or space between cutoff dates and the forecast *horizon* 
                in each cross-validation step.
                '''),
                   
                   
            html.H3("4. Results",
                    style = {'color': 'blue'}),
            dcc.Markdown(
                '''
                \n * The first graph shows the probabilistic predictions of future 
                observations for the specified forecast period. \n * The second graph 
                plots the chosen performance metrics against the prediction horizon. 
                The mean of the performance metric is taken over 
                a 10% rolling window of the points. \n * Numerical results for both plots can be exported.
                 
                '''),
                
                
              html.Hr(),
              
              html.Div([
                  html.Span(["Carlos J Peña",
                  html.Br(),
                  "Jr. Biologist & Biostatistician", 
                  
                  html.Br(),
                  "Greater Bilbao, Basque Country - Spain"
                  ],
                  
                  style={'font-family': 'Calibri', 'font-size':'16px',
                         'color':'#31557F', 'text-align': 'center'}
                  ),
                  html.Br(),
                  html.Br(),
                  
                  html.A(
             html.Img(src="https://github.githubassets.com/images/modules/site/icons/footer/linkedin.svg", 
                     style={'width':'20px'}),
             href="https://www.linkedin.com/in/carljpena8/?viewAsMember=true"),
            
            html.A(
             html.Img(src="https://github.githubassets.com/images/modules/site/icons/footer/github-mark.svg", 
                      style={'width':'20 px'}),
             href="https://github.com/carlosjps")
        
                ],
        style = { 'text-align': 'center'}),
       
    
    html.Br() 
                   
                  
                        
            
            
            
            
            
            ])

]) 
                
    ], 
                style={
                    'width': '85%',
                    #'max-width': '1440',
                    'margin-left': 'auto',
                    'margin-right': 'auto',
                    'margin-top': '20px',
                    'margin-bottom': '10px'}
                )
    
# Functions

# file upload function
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return None

    return df


# callback table creation
@app.callback([Output('dropdown_table_filterDate', 'options'),
               Output('dropdown_table_filterResponse', 'options'),
               Output('result-intermedio', 'children')],
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename')])
def update_output( contents, filename):
    if contents is not None:
        df = parse_contents(contents, filename)
        dff = {'df1': df.to_json(orient='split')}
        if df is not None:
            return [{'label': i, 'value': i} for i in sorted(list(df))], [{'label': i, 'value': i} for i in sorted(list(df))], json.dumps(dff)
        else:
                return [], [], []
    else:
        return [], [], []



#callback update options of filter dropdown
@app.callback([Output('plot', 'figure'),
               Output('predictions-table', 'data'),
               Output('predictions-table', 'columns'),
               Output('result-cv-intermedio', 'children'),
               Output('result-posteriorsamples-intermedio', 'children')],
              [Input('propagate-button', 'n_clicks'),
               State('result-intermedio', 'children'),
               State('dropdown_table_filterDate', 'value'),
               State('dropdown_table_filterResponse', 'value'),
               State("endate", "date"), 
               State('initial', 'value'),
               State('period', 'value'),
               State("horizon", "value")])
def create_forecast(n_clicks_update, df_uploaded, dropdown_date, dropdown_resp, endate, initial, period, horizon):
    if n_clicks_update is not None: 
        df_upload = json.loads(df_uploaded) 
        df_upload = pd.read_json(df_upload['df1'], orient='split')
        
        df_upload = df_upload[[dropdown_date, dropdown_resp]]
        
        ## Rename columns
        dff = df_upload.rename(columns = {dropdown_date: "ds", dropdown_resp: "y"})
            
        dff.set_index("ds", inplace = True, drop = False)
        
            
        endate = datetime.strptime(endate, "%Y-%m-%d")
            


        #q = all_options["percentiles"]            
        #q = [percentiles/ 100 for percentiles in q]
        
        muestras_predict, cross_val = f.ejecutar_modelo(dff, fecha_fin=endate, initial=initial,
                                                        period=period, horizon=horizon)
        
        crossval = {'df1': cross_val.to_json(orient='split')}
        
        posterior_samples = {'df1': muestras_predict.to_json(orient='split')}
        
        result = f.quant(muestras_predict)
        result.insert(loc=0, column="Date", value= result.index.date)

        
        
        
        
        go_scatter = go.Scatter(name = "Mean", x=result.index, y=result["mean"])
        go_sup = go.Scatter(name = "Upper Pred Int 95%",
                                x=result.index,
                                y = result["upper_predic_interval_95"],
                                line=dict(width=0),
                                fillcolor='rgba(0,100,80,0.2)',
                            hoverinfo="all", showlegend=False)
        
        go_int95 = go.Scatter(name= "Prediction Interval 95%",
                            x=result.index,
                            y=result["lower_predic_interval_95"], fill='tonexty',
                            fillcolor='rgba(0,100,80,0.2)', line=dict(width=0), hoverinfo="all",
                            showlegend=True)
        
        go_inf = go.Scatter(name= "Lower Pred Int 95%",
                            x=result.index,
                            y=result["lower_predic_interval_95"], #fill='tonexty',
                            fillcolor='rgba(0,100,80,0.2)', line=dict(width=0), hoverinfo="all",
                            showlegend=False)
        
        go_sup50 = go.Scatter(name = "Upper Pred Int 50%",
                                x=result.index,
                                y = result["upper_predic_interval_50"],
                                line=dict(width=0),
                                fillcolor='rgba(0,100,80,0.2)',
                            hoverinfo="all", showlegend=False)
        
        go_int50 = go.Scatter(name= "Prediction Interval 50%",
                            x=result.index,
                            y=result["lower_predic_interval_50"], fill='tonexty',
                            fillcolor='rgba(0,100,80,0.2)', line=dict(width=0), hoverinfo="all",
                            showlegend=True)
        
        go_inf50 = go.Scatter(name= "Lower Pred Int 50%",
                            x=result.index,
                            y=result["lower_predic_interval_50"], #fill='tonexty',
                            fillcolor='rgba(0,100,80,0.2)', line=dict(width=0), hoverinfo="all",
                            showlegend=False)
                    
                    
        fig_list = [go_scatter, go_sup, go_int95, go_inf, go_sup50, go_int50, go_inf50]
        
                
        fig_vols = go.Figure(fig_list)
        fig_vols.update_layout(yaxis_title = dropdown_resp,
                               xaxis_title= "Date", hovermode = "closest", 
                               title = "Quantile Predictions") 
        

    

        return fig_vols, result.to_dict('records'), [{'name': i, 'id': i} for i in result.columns], json.dumps(crossval), json.dumps(posterior_samples)

    
    else:
        raise PreventUpdate


                                  


@app.callback([Output('plot-cv', 'figure'),
               Output('table-cv', 'data'),
               Output('table-cv', 'columns')],
              [Input('cv-button', 'n_clicks'),
               State('result-cv-intermedio', 'children'),
               State('dropdown-metric','value')
               #State('dropdown_table_filterDate', 'value'),
               #State('dropdown_table_filterResponse', 'value'),
               #State('initial', 'value'),
               #State('period', 'value'),
               #State("horizon", "date")
               ])
def cross_validate(n_clicks_update, crossval, metric):
    if n_clicks_update is not None:
        df_cv = json.loads(crossval) 
        df_cv= pd.read_json(df_cv['df1'], orient='split')
        
        df_p = performance_metrics(df_cv, rolling_window=0.1)
        
        ## I do not know why 'horizon' is converted to milliseconds
        ## Let's convert it back to DAYS!!
        
        df_p['horizon'] = df_p['horizon']/(24*60*60*1000)

        
        
        ## PLOT CROSS VALIDATION PERFORMANCE METRIC ACCORDING TO HORIZON
        go_crossval = go.Scatter(name = metric, x=df_p.horizon, y=df_p[metric])
        
        fig_cv = go.Figure(go_crossval)
        fig_cv.update_layout(yaxis_title = metric,
                               xaxis_title= "Horizon (days)", hovermode = "closest", 
                               title = "Performance metric by horizon") 
        
        return  fig_cv, df_p.to_dict('records'), [{'name': i, 'id': i} for i in df_p.columns]
 
        
        
        
    else: 
        raise PreventUpdate
      
        
        












if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=True)
