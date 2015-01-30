<html>
    <head>
        <title>Switchlight</title>
        <link rel="icon" type="image/png" href="/favicon" />
        <link rel="apple-touch-icon-precomposed" href="images/switch-large.png">
        <style type="text/css">
            body {font-size: 200%; font-family: monospace; text-align: center;}
            a {color: #000000;}
            .active {color: green;}
            .inactive {color: black;}
        </style>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
        <meta http-equiv="refresh" content="10">
    </head>
    <body>
        <div style="width: 100%; max-width: 500px; margin-left: auto; margin-right: auto">
            <img src="images/switchlight.svg"/>
        </div>
        <br>
        % for sw in switches:
            <p>{{sw.name}}<br>
            %for state in sw.states:
                %if state == sw.states[sw.status]: c = 'active'
                %else: c = 'inactive'
                %end
                <a class="{{c}}" href="/set/{{sw.name}}/{{state}}">{{state}}</a><br>
            %end
            </p>
        % end
        <br><br>
        % if timers:
            <h2>Timers</h2>
            % for t in timers:
                <p><b>{{t[0]}}</b> - (<a href="/cancel/{{t[3]}}" style="color: #FF0000">cancel</a>)</p>
                % for a in t[1]:
                    <p>{{a[0]}}: {{a[1]}}</p>
                % end
                % if t[2]:
                    <p>Lock Switchlight</p>
                % end
            % end
        % end

        <p><a href='/settimer'>Set Timer</a></p>
        <p><a href='/lock'>Lock</a></p>
    </body>
</html>
