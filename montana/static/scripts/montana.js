$(document).ready(function() {

    var body = $('body');

    $.getJSON('api/services', function(data) {

        $.each(data.services, function(i, service) {
            body.append($('<p>Recent "' + service.service + '" events:</p>'));
            var list = $('<ul>').appendTo(body);
            $.getJSON(service.events, function(data) {
                $.each(data.events, function(i, event) {
                    list.append($('<li>').text(event.logged + ': ' + event.status));
                });
            });
        });

    });

});
