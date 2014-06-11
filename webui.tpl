<html>
    <head>
        <title>Switchlight</title>
        <style type="text/css">
            body {font-size: 200%; font-family: monospace; text-align: center;}
            a {color: #000000;}
        </style>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
        <meta http-equiv="refresh" content="5">
    </head>
    <body>
        <h1>Switchlight</h1>
        <br>
        % for sw in switches:
            % if sw[1] == 'on':
                % c = '#00FF00'
            % elif sw[1] == 'off':
                % c = '#FF0000'
            % end
            <p style="color: {{c}}"><a href="/set/{{sw[0]}}">{{sw[0]}}</a><br> {{sw[1]}}</p>
        % end
    </body>
</html>
