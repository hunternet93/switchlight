<html>
    <head>
        <title>Switchlight - Locked</title>
        <style type="text/css">
            body {font-size: 200%; font-family: monospace; text-align: center;}
            a {color: #000000;}
        </style>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    </head>
    <body>
        <div style="width: 100%; max-width: 500px; margin-left: auto; margin-right: auto">
            <img src="/logo.svg"/>
        </div>
        <br>
        <form name="settimer" action="/settimer" method="post">
            <p>
                Turn switches
                <input type="radio" name="switchmode" value="1"><span style="color: #00FF00">On</span>
                <input type="radio" name="switchmode" value="0" checked><span style="color: #FF0000">Off</span>
            </p>
            <p> Switches: </p>
            % for s in switches:
                <p><input type="checkbox" name="switches" value="{{s}}">{{s}}</p>
            % end
            <p><input type="checkbox" name="lock" value="1">Lock Switchlight</p>
            <br>
            <p>
                Hours:
                <select name="hours">
                    % for h in range(0,12):
                        <option value="{{h}}">{{h}}</option>
                    % end
                </select>
            </p>
            <p>
                Minutes:
                <select name="minutes">
                    % for m in range(5,60,5):
                        <option value="{{m}}">{{m}}</option>
                    % end
                </select>
            </p>
            <input type="submit" value="Set Timer">
        </form>
        <a href="/" style="color: #FF0000">Cancel</a>
    </body>
</html>
