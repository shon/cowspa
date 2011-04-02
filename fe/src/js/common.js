function popup_login(prev_req) {
    var login_form = $('relogin_form');
    var msgbox = $('relogin_msg');
    login_form.MooDialog();
    
    var request = new JSONRequest({
        url: '/login',
        onRequest: function(){
            msgbox.set('text', 'Logging in ...');
        },
        on_success: function(result, responseText) {
            var cur_uri = new URI();
            cur_uri.set('directory', '');
            cur_uri.set('file', result);
            cur_uri.go();
        },
        on_fail: function(result) {
            msgbox.set('text', "Try again..");
        }
    });

    $('re_login').addEvent('click', function(e) {
        request.postform('relogin_form');
    });
};

var JSONRequest = new Class ({
    Extends: Request.JSON,
    initialize: function(options){
        //options['Content-Type'] = 'application/json';
        options['method'] = 'post';
        options['urlEncoded'] = false;
        this.on_success = options['on_success'];
        this.parent(options);
    },
    onSuccess: function(responseJSON, responseText) {
        var retcode = responseJSON['retcode'];
        var result = responseJSON['result'];
        // console.log(responseJSON);
        // console.log(result);
        if ((retcode == 0) && (this.success != null)) {
            this.on_success(result, responseText);
        } else if (retcode == 2) {
            if (this.on_fail != null) {
                this.on_fail(result);
            } else {
                popup_login(this);
            };
        } else if (retcode != 0) {
            if (this.on_fail != null) {
                this.on_fail(result);
            };
        };
    },
    postform: function(form_id) {
        var data = $(form_id).toQueryString().parseQueryString();
        //console.log(data);
        this.json_send(data);
    },
    json_send: function(data) {
        console.log(data);
        console.log(JSON.encode(data));
        this.setHeader('Content-Type', 'application/json');
        this.send(JSON.encode(data));
    },
});
