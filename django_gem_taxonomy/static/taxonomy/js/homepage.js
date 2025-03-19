function validate_string(obj)
{
    tax_in = $($(obj).find('input[name="validate_input"]')[0]).val();
    $.ajax({
        url: "taxonomy/api/v1/validation/" + tax_in
    }).done(function(data) {
        $('div[name="validate_output"]').css('display', '');
        $('div[name="validate_output"]').empty();
        if (data['success'] == true && data['is_canonical'] == true) {
            $('div[name="validate_output"]').append('<p style="font-weight: bold;">Result: <span style="color: green;">&#x2B24;</span></p><p>Input: ' + tax_in + '</p><p>Validation: Success</p><p>Canonical Form: True</p>');
        }
        else if (data['success'] == true && data['is_canonical'] == false) {
            $('div[name="validate_output"]').append('<p style="font-weight: bold;">Result: <span style="color: orange;">&#x2B24;</span></p><p>Input: ' + tax_in + '</p><p>Validation: Success</p><p>Is Canonical: False</p><p>Canonical form: ' + data['canonical']);
        }
    }).fail(function(data) {
        $('div[name="validate_output"]').css('display', '');
        $('div[name="validate_output"]').empty();
        $('div[name="validate_output"]').append('<p style="font-weight: bold;">Result: <span style="color: red;">&#x2B24;</span></p><p>Input: ' + tax_in + '</p><p>Validation: Failed</p><p>Message: ' + data.responseJSON['message'] + '</p>');
    })
}

function explain_string(obj)
{
    tax_in = $($(obj).find('input[name="explain_input"]')[0]).val();
    $.ajax({
        url: "taxonomy/api/v1/explanation/" + tax_in,
        data: {fmt:'textmultiline'}
    }).done(function(data) {
        $('div[name="explain_output"]').css('display', '');
        $('div[name="explain_output"]').empty();

        if (data['success'] == true) {
            var n_lines = data['explanation'].split(/\r\n|\r|\n/).length;
            $('div[name="explain_output"]').append('<p style="font-weight: bold;">Result: <span style="color: green;">&#x2B24;</span></p>').append($('<textarea style="width: 100%;" rows="' + n_lines + '"/>').val(data['explanation']));
        }
    }).fail(function(data) {
        $('div[name="explain_output"]').css('display', '');
        $('div[name="explain_output"]').empty();
        $('div[name="explain_output"]').append('<p style="font-weight: bold;">Result: <span style="color: red;">&#x2B24;</span></p><p>Input: ' + tax_in + '</p><p>Explain: Failed</p><p>Message: ' + data.responseJSON['message'] + '</p>');
    })
}

function reset_subareas()
{
    $("div.accordion").css('display', 'none');
    $("div[name='validate_output']").css('display', 'none');
    $("div[name='validate_output']").empty();
    $("input[name='validate_input']").val('');

    $("div[name='explain_output']").css('display','none');
    $("div[name='explain_output']").empty();
    $("input[name='explain_input']").val('');

}

// $('input[name=\'validate_input\']).val(\'\')
