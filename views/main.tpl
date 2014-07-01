<html>
    <head>
        <title>Switchlight</title>
        <style type="text/css">
            body {font-size: 200%; font-family: monospace; text-align: center;}
            a {color: #000000;}
        </style>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
        <meta http-equiv="refresh" content="10">
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
        <br><br>
        % if timers:
            <h2>Timers</h2>
            % for t in timers:
                <p><b>{{t[0]}}</b> - (<a href="/cancel/{{t[3]}}" style="color: #FF0000">cancel</a>)</p>
                % for a in t[1]:
                    <p>{{a[0]}}: 
                    % if a[1]:
                        <span style="color: #00FF00">On</span>
                    % else:
                        <span style="color: #FF0000">Off</span>
                    % end
                    </p>
                % end
                % if t[2]:
                    <p>Lock Switchlight</p>
                % end
            % end
        % end
        <br><br>
        <p><a href='/settimer'>Set Timer</a></p>
        <p><a href='/lock'>Lock</a></p>
    </body>
</html>
