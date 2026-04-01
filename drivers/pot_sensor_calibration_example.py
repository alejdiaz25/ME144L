import numpy as np 
import matplotlib.pyplot as plt 
from sklearn.linear_model import LinearRegression 

# An example Python code for linear regression
# specific for building a linear calibration of a potentiometer sensor in
# ME 144L pendulum lab
# Fall 2022 version (ER 16 Sep 2022)
# NOTE: the data can be entered on lines 47-50
# The b0 coefficient is the 'y intercept [deg]'
# the b1 coefficient is the 'K value in [deg/Int]' (a calibration coefficient)
#
  
def estimate_coef(x, y): 
    # number of observations/points 
    n = np.size(x) 
  
    # mean of x and y vector 
    m_x, m_y = np.mean(x), np.mean(y) 
  
    # calculating cross-deviation and deviation about x 
    SS_xy = np.sum(y*x) - n*m_y*m_x 
    SS_xx = np.sum(x*x) - n*m_x*m_x 
  
    # calculating regression coefficients 
    b_1 = SS_xy / SS_xx 
    b_0 = m_y - b_1*m_x 
  
    return(b_0, b_1) 
  
def plot_regression_line(x, y, b): 
    # plotting the actual points as scatter plot 
    plt.scatter(x, y, color = "m", 
               marker = "o", s = 50) 
  
    # predicted response vector 
    y_pred = b[0] + b[1]*x 
  
    # plotting the regression line 
    plt.plot(x, y_pred, color = "g") 
  
    # putting labels 
    plt.xlabel('Integer') 
    plt.ylabel('Angular displacement [deg]') 
    plt.legend(['Raw Data','Linear Fit'])
  
    # function to show plot 
    plt.show() 
  
def main(): 
    # observations from calibration experimentss
    y = np.array([-89.7, -45.3, 0.3, 45.4, 89.9]) # angle in deg
    x = np.array([0.43, 1.31, 2.46, 3.54, 4.26]) # Integer reading
  
    # estimating coefficients 
    b = estimate_coef(x, y) 
    print("Estimated coefficients:\nb_0 = {} \nb_1 = {}".format(b[0], b[1]))
  
    # plotting regression line 
    plot_regression_line(x, y, b) 
    
    
    xval = x.reshape(-1,1)
    model = LinearRegression().fit(xval, y)
    R2    = model.score(xval, y)
    slope, intc = float(model.coef_), float(model.intercept_)
    print('\n')
    print('Slope [deg/Int]:', slope)
    print('Intercept [deg]:', intc)
    print('R^2:', R2)
    # plt.plot(x,slope*x + intc,'r--', x, y,'b--')
    
    
    
    
  
if __name__ == "__main__": 
    main() 