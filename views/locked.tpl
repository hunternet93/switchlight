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
        <p><b>Switchlight is locked.</b></p>
        <p>Enter the passcode to unlock</p>
        % if incorrect:
            <p style="color: #FF0000"><b>Incorrect Passcode</b></p>
        % end
        <form name="passcode" action="unlock" method="post">
            <input type="password" name="code">
            <input type="submit" value="Unlock">
        </form>
    </body>
</html>
