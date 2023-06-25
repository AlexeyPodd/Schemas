schemaSlugs.forEach((slug) => {
    const deletionLink = document.getElementById(`link-deletion-schema-${slug}`);

    deletionLink.addEventListener('click', function(event) {
        event.preventDefault();

        const confirmDelete = window.confirm("Are you sure you want to delete Schema?")

        if (confirmDelete) {
            $.ajax({
                type: 'POST',
                url: deleteSchemaUrl,
                data: {
                    csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
                    schema: slug,
                },
                success: function() {
                    const schemaRow = deletionLink.parentNode.parentNode.parentNode;
                    schemaRow.parentNode.removeChild(schemaRow);
                }
            });
        }
    });
});