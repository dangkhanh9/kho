

# Time Series Quantile Forecasting Dashboard

The dashboard created is the outcome of my modest attempt to build my first Dash app and it aims to generate quantile forecasts for **continuous**, **daily** time series data.  

The idea behind this concept is that we can think of the future value of a time series as a random variable, and get different quantiles from its distribution. In a Bayesian framework, this distribution is known as the *posterior predictive distribution* (PPD). 

In other words, the term *quantile forecast* implies that we are no longer focusing on the estimation of the conditional mean of the response variable (the usual point forecast).

## Forecasting model

The forecasting framework implemented is the *prophet* procedure developed by [Facebook](https://facebook.github.io/prophet/).  
All of the specific details for this modeling technique can be found at the [prophet documentation](https://facebook.github.io/prophet/) and the paper [*Forecasting at scale*](forecasting_at_scale_prophetFB.pdf). 
                         
I highly recommend a thorough analysis of the documentation to understand more about this model.

Explore my dashboard deployed at [heroku](https://ts-quantile-forecast.herokuapp.com) with your own data (REMEMBER: At this moment, daily datasets only).

## Diagnostics section

Time series cross-validation is [computationally expensive](https://examples.dask.org/applications/forecasting-with-prophet.html). For this reason, the memory limitation in the free version of Heroku may crash the app and not display any results.  
Therefore, it would be wise not to select the option to perform cross validation at Heroku. Instead, download the app code files (*code_app.py* and *functions_app.py*) and install the dependencies (*requirements.txt*) in a virtual environment in order to **run the app locally where memory limits are less restricted**.
