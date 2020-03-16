$('#delete-feedback-confirm-modal').on('show.bs.modal', function(event) {
    let feedbackData = $(event.relatedTarget).parent();
    let feedbackId = feedbackData.data('feedback-id');
    let feedbackClass = feedbackData.data('feedback-class');
    let modal = $(this);
    modal.find('.modal-body').html(`Are you sure you want to delete the feedback for the class <strong>&ldquo;${feedbackClass}&rdquo;</strong>? You can&rsquo;t undo this action.`);
    modal.find('#confirm-delete-feedback-button').data('feedback-id', feedbackId);
});

$('#confirm-delete-feedback-button').click(() => {
    let feedbackId = $('#confirm-delete-feedback-button').data('feedback-id');
    $.post('/feedback/delete', { id: feedbackId }, resp => {
        if (resp.code === 0) {
            // Hide popup modal
            $('#delete-feedback-confirm-modal').modal('hide');
            // Delete corresponding card element
            $(`.card-links-container[data-feedback-id=${feedbackId}]`).parent().parent().remove();
        }
    });
});
