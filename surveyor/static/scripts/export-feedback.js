$('#check-all').click(function() {
    $('.class-checkbox').not(this).prop('checked', this.checked);
    if (this.checked) {
        $(this).next().children().html('Deselect all classes');
    } else {
        $(this).next().children().html('Select all classes');
    }
});

$('#export-form').submit(() => {
    $('#download-msg').show();
});
