<html>
    <head>
        <title>Switchlight</title>
        <style type="text/css">
            body {font-size: 200%; font-family: monospace; text-align: center;}
            a {color: #000000;}
        </style>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
        % if not locked:
            <meta http-equiv="refresh" content="5">
        % end
    </head>
    <body>
        <h1>Switchlight</h1>
        <br>
        % if locked:
            <p><b>Switchlight is locked.</b></p>
            <p>Enter the passcode to unlock</p>
            <form name="passcode" action="unlock" method="post">
                <input type="password" name="code">
                <input type="submit" value="Enter">
            </form>
        % else:
            % for sw in switches:
                % if sw[1] == 'on':
                    % c = '#00FF00'
                % elif sw[1] == 'off':
                    % c = '#FF0000'
                % end
                <p style="color: {{c}}"><a href="/set/{{sw[0]}}">{{sw[0]}}</a><br> {{sw[1]}}</p>
            % end
            <br><br><br>
            </p><a href='/lock'>Lock</a></p>
        % end
    </body>
</html>
