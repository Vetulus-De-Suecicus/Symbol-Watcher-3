# Symbol Watcher 3
![Screenshot](https://github.com/Vetulus-De-Suecicus/Symbol-Watcher-3/blob/main/Images/Screenshot.png?raw=true)
Portfolio and graph tool for stocks built on textual, textual-plot and yfinance<br/>
<br/>
OBSERVE!<br/>
!. Add the stocks you are interested in - within the holdings.json file, you can specify the amount of ie. stocks you have bought and for what price in your local currency <br/>
```
    {
        "SYMBOL": [QUANTITY OF STOCKS, CLOSING PRICE BOUGHT],
        "SSAB-B.ST": [150, 55.95],
        "^OMX": [0, 0],
        "MSFT": [1, 500],
        "AAPL": [0, 0],
        "AMZN": [0, 0]
    }
```
!. Configure the app as you wish via the settings.json file<br/>
<br/>
PERIOD - Controls for how long you want the plots to show data for.<br/>
INTERVAL - Controls the granularity.<br/>
UPDATE_INTERVAL - Controls how often the prices are updated.<br/>
LOCAL_CURRENCY - Controls the currency conversion for the total portfolio worth calulcations.<br/>
<br/>
Remember to always set LOCAL_CURRENCY to the currency you wish to have the app display and convert to - for you.<br/>
```
    {
        "PERIOD": "1d",
        "INTERVAL": "1m",
        "UPDATE_INTERVAL": 60,
        "LOCAL_CURRENCY": "SEK"
    }
```

<br/>
TODO:<br/>
Work on what AI told me to do :p<br/>
<br/>
Special thanks to:<br/>
Fashoomp, <br/>
David Fokkema, <br/>
Edward Jazzhands, <br/>
Will McGugan<br/>
<br/>
<br/>
