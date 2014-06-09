<html>
    <head>
        <title>Switchlight</title>
        <style type="text/css">
            body {font-size: 200%; font-family: monospace; text-align: center;}
            a {color: #000000;}
        </style>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    </head>
    <body>
        <h1>Switchlight</h1>
        <br>
        % for sw in switches:
            % if sw[2] == 'on':
                % c = '#00FF00'
            % elif sw[2] == 'off':
                % c = '#FF0000'
            % end
            <p style="color: {{c}}"><a href="/set/{{sw[1]}}">{{sw[0]}}</a><br> {{sw[2]}}</p>
        % end
    </body>
</html>
