#!/usr/bin/env python
# coding: utf-8

from datetime import datetime 

from prophet import Prophet
from prophet.diagnostics import cross_validation

import os
import pandas as pd








##=======================FUNCTION 1=============================================##
## FITTING PROPHET MODEL AND GENERATION OF SAMPLES FROM PREDICTIVE POSTERIOR DISTRIBUTION
##=============================================================================##

###########################################################################
######In order to suppress the messages when fitting model #########
##########################################################################

class suppress_stdout_stderr(object):
    '''
    https://github.com/facebook/prophet/issues/223
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).

    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])

#############################################################################

def ejecutar_modelo(serie,fecha_fin, initial, period, horizon, **kwargs):
    
    modelo = Prophet(changepoint_prior_scale=0.01, # por defecto es 0.05. Determina la felixibilidad de la tendencia
                    seasonality_mode='additive', # estacionalidad aditiva
                    seasonality_prior_scale= 10, # por defecto es 10. # Controla la flexibilidad de la estacionalidad 
                    yearly_seasonality=True, # existencia de estacionalidad anual
                    weekly_seasonality=False, # no estacionalidad semanal
                    daily_seasonality=False, # ni estacionalidad diaria
                    uncertainty_samples=1e3, #defecto es 1000, Numero de muestras utilizadas para estimar el intervalo de predicción.
# uncertainty samples también nos permite seleccionar el número de muestras a extraer en la distribución predictiva posterior.
                    interval_width = 0.95) #Esto dará predicciones con un intervalo al 95% (2.5% a 97.5%).
    
    with suppress_stdout_stderr():
        modelo.fit(serie)
    
    #anyos = fecha_fin.year - serie.ds.max().year # Número de años a predecir
    fechas = pd.date_range(start = serie.ds.max() + pd.Timedelta(1, unit="day"),
                           end = datetime.strptime(str(fecha_fin.day)+"-"+str(fecha_fin.month)+"-"+str(fecha_fin.year), "%d-%m-%Y"),
                           #periods = round(365.25*anyos), #periodos = 365.25 * el número de años a predecir 
                           freq="D") # frecuencia diaria
    futuro = pd.DataFrame({'ds': fechas})
    
    predsamples = modelo.predictive_samples(futuro)
    
    yhat_predsamples = pd.DataFrame(predsamples["yhat"], 
                                  index = futuro.ds)
    
    df_cv = cross_validation(modelo, initial=str(initial)+'days', period=str(period)+'days', horizon = str(horizon)+'days', parallel="processes") 
    
    return yhat_predsamples, df_cv



##=======================FUNCTION 2=============================================##

##=============================================================================##

def quant(muestras_predict):
    """
    Computation of mean estimation and quantiles for the samples drawn from the 
    predictive posterior distributions
    ----------
    INPUT/Entrada
    ----------
    muestras_predict: pd.DataFrame with samples drawn from PPD.
        
    -------
    OUTPUT/Salida
    -------
    pd.DataFrames:
    mean estimation, and several quantiles
    """
    
    postpred = muestras_predict.apply(lambda x: x.quantile([0, 0.025, 0.25, 0.5, 0.75, 0.975, 1]), axis =1)
    postpred.rename(columns={0:"min", 0.025: "lower_predic_interval_95", 0.25:"lower_predic_interval_50",
                             0.5:"median", 0.75:"upper_predic_interval_50",0.975:"upper_predic_interval_95", 1: "max"}, inplace=True)
    
    postpred['mean'] = postpred.mean(axis=1)
    
    return postpred


