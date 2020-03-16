$('.feedback').click(function(event) {
    let feedback = $(this);
    console.log(feedback, feedback.find('.blockquote-body'));
    let feedbackContent = feedback.find('.blockquote-body').html();
    let feedbackAuthor = feedback.find('.blockquote-footer').html();
    let modal = $('#feedback-details-modal');
    modal.find('.blockquote-body').html(feedbackContent);
    modal.find('.blockquote-footer').html(feedbackAuthor);
    modal.modal('show');
});
