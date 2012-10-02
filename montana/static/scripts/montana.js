$(document).ready(function() {
    // Todo: Cleanup.
    $('li.event').tooltipsy({delay: 0, offset: [0, 10]});
    $('a[rel*=modal]').leanModal({top: 200});
    $('form').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        var request = $.ajax({type: form.attr('method'),
                              url: form.attr('action'),
                              data: {name: $('input[name="name"]', form).val(),
                                     description: $('input[name="description"]', form).val(),
                                     key: $('input[name="key"]', form).val()},
                              dataType: 'json'});
        request.success(function(response) {
            $('a', form.parent().prev()).text($('input[name="description"]', form).val());
            $('input[name="key"]').val($('input[name="key"]', form).val());
            localStorage.setItem('api-key', $('input[name="key"]', form).val());
            $('#lean_overlay').click();
        });
        request.error(function(request) {
            $('p.status', form).remove();
            var status = $('<p class="status">').appendTo(form);
            try {
                status.text($.parseJSON(request.responseText).error.message);
            } catch(e) {
                status.text(request.statusText);
            }
            $('#lean_overlay').click(function() {
                status.remove();
            });
        });
    });
    $('input').keypress(function(e) {
        if (e.which == 13) {
            e.preventDefault();
            $(this).closest('form').submit();
        }
    });
    $('input[name="key"]').val(localStorage.getItem('api-key'));
});
