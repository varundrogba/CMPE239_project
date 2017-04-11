
from flask import Flask, render_template, request
from bson.json_util import dumps
from Data_parser import DataParser, ListAttribute
from regression import Regression
import numpy as np
from numpy import newaxis


app = Flask(__name__)


@app.route("/")
def index():
   return render_template("index.html")

@app.route('/AvgMonthTemp', methods=['POST','GET'])
def AvgMonthTempList():           
    """
    get the list of data for specific city, country and Month
    Data is returned as a list of list
    Returned list contains data in this format: [ [training_x], [training_y], [test_x], [test_y], [predictLine_x], [predictLine_y]]
    """
    try:
        p = dataFrame.getDataForCityCountryMonth(City=request.form['City'], Country=request.form['Country'], Month=request.form['Month'])
        yearList, avgTempList = dataFrame.SplitYearAvgTemp( p )
        avgTempList = np.array(avgTempList).astype(np.float)
        yearList = np.array(yearList).astype(np.float)
        training_x, training_y, test_x, test_y, predictLine_x, predictLine_y = regression.fnLinearRegression1(yearList, avgTempList)
        return dumps({"training_x":training_x, "training_y":training_y, "test_x":test_x, "test_y":test_y, "predictLine_x":predictLine_x, "predictLine_y":predictLine_y})
    except:
        return "error"


@app.route('/AvgTempForSpecifiedMonth', methods=['POST','GET'])
def AvgTempForSpecifiedMonth():          
    """
    return avg temperature for specified month/year/country/city.
    returned data is in float.
    """ 
    try:

        temp, pList = dataFrame.getTemperature(City=request.form['City'], Country=request.form['Country'], Month=request.form['Month'], Year=request.form['Year'])      

        #if temp is found in database, return the temperature
        if temp > -9999:
            print "actual"
            return dumps(temp)
        #if temp is not found in database, predict it using regression
        else:
            yearList, avgTempList = dataFrame.SplitYearAvgTemp( pList )
            avgTempList = np.array(avgTempList).astype(np.float)
            yearList = np.array(yearList).astype(np.float)
            pYear = float(request.form['Year'])
            predictYear = []
            predictYear.append(pYear)

            scoreReg, PvalueReg = regression.fnLinearRegression(yearList, avgTempList, predictYear)
            scoreIso, PvalueIso = regression.fnIsotonicRegression(yearList, avgTempList, predictYear)
            scoreBR, PvalueBR =  regression.fnBayesianRidge(yearList, avgTempList, predictYear)
            scoreRR, PvalueRR = regression.fnRANSACRegressor(yearList, avgTempList, predictYear)
            scoreGP, PvalueGP = regression.fnGaussianProcessRegressor(yearList, avgTempList, predictYear)
            scoreSV, PvalueSV = regression.fnSVR(yearList, avgTempList, predictYear)

            score = np.array([scoreReg, scoreIso, scoreBR, scoreRR, scoreGP, scoreSV])
            pValue = np.array([PvalueReg, PvalueIso, PvalueBR, PvalueRR, PvalueGP, PvalueSV])

            pValue = pValue[np.logical_not(np.isnan(pValue))]
            score = score[np.logical_not(np.isnan(pValue))]           

            maxScoreIndex = np.argmax(score)

            

        return dumps({"avgTemp" : pValue[maxScoreIndex]})
    except:
        return "error"




if __name__ == '__main__':    
    global dataFrame
    global regression
    dataFrame = DataParser()    
    regression = Regression()
    app.run()