// Adding column forms script
const addColumnBtn = document.getElementById('add-column')
const totalForms = document.getElementById('id_columns-TOTAL_FORMS')
addColumnBtn.addEventListener('click', add_new_form)

function add_new_form(event) {
    event.preventDefault();

    const currentColumnForms = document.getElementsByClassName('column-form')
    const currentColumnsCount = currentColumnForms.length
    const formCopyTarget = document.getElementById('column-form-list')
    const EmptyFormEl = document.getElementById('empty-form')
    const copyEmptyFormEl = EmptyFormEl.cloneNode(true)

    copyEmptyFormEl.setAttribute('class', 'column-form col-12 p-3')
    copyEmptyFormEl.setAttribute('id', '')
    const regex = new RegExp('__prefix__', 'g')
    copyEmptyFormEl.innerHTML = copyEmptyFormEl.innerHTML.replace(regex, currentColumnsCount)

    totalForms.setAttribute('value', currentColumnsCount + 1)

    const originalInputs = EmptyFormEl.querySelectorAll('input, select')
    const clonedInputs = copyEmptyFormEl.querySelectorAll('input, select')

    for (let i = 0; i < originalInputs.length; i++) {
        const originalElement = originalInputs[i]
        const clonedElement = clonedInputs[i]

        clonedElement.value = originalElement.value

        if (originalElement.id === 'id_columns-__prefix__-ORDER') {
            clonedElement.value = currentColumnsCount + 1
        }

        originalElement.value = ''
    }

    // Clearing (deleting) limit fields for original empty form
    updateInputs('__prefix__', "")

    // Adding deletion link
    const deletionLink = document.createElement('a');
    deletionLink.href = '#';
    deletionLink.textContent = 'Delete';
    deletionLink.setAttribute('class', 'link-danger link-underline-opacity-0')

    const deletionLinkContainer = document.createElement('div');
    deletionLinkContainer.setAttribute('class', `col-1 deletion-form-${currentColumnsCount}-link`);
    deletionLinkContainer.appendChild(deletionLink);

    const inputsRow = copyEmptyFormEl.querySelector(':scope > :last-child');
    inputsRow.removeChild(inputsRow.querySelector(':scope > :last-child'));
    inputsRow.appendChild(deletionLinkContainer);

    // Adding new form to formset
    formCopyTarget.append(copyEmptyFormEl);

    // Adding listener of selected data type for limit fields for added forms
    const dataTypeSelect = document.getElementById(`id_columns-${currentColumnsCount}-data_type`);
    dataTypeSelect.addEventListener('change', function () {
        updateInputs(currentColumnsCount, dataTypeSelect.value);
    });

    // Adding listener of deletion link
    deletionLink.addEventListener('click', function(event) {
        event.preventDefault();
        markDeletionAndHide(currentColumnsCount, deletionLink);
    })
}

// Adding or deleting limit fields to forms
for (let i = -1; i < totalForms.value; i++) {
    let formNumber;
    if ( i === -1) {
        formNumber = '__prefix__';
    } else {
        formNumber = i;
    }

    const dataTypeSelect = document.getElementById(`id_columns-${formNumber}-data_type`);
    dataTypeSelect.addEventListener('change', function () {
        updateInputs(formNumber, dataTypeSelect.value);
    });
}

function updateInputs(numberOfForm, selectedValue) {
    const minimalInputContainer = document.getElementById(`minimal-input-${numberOfForm}-container`);
    const maximalInputContainer = document.getElementById(`maximal-input-${numberOfForm}-container`);
    const minimalLabelContainer = document.getElementById(`minimal-label-${numberOfForm}-container`);
    const maximalLabelContainer = document.getElementById(`maximal-label-${numberOfForm}-container`);

    const isLimitedDataType = valuesDataTypeNeedLimit.includes(selectedValue)

    minimalInputContainer.innerHTML = '';
    maximalInputContainer.innerHTML = '';
    minimalLabelContainer.innerHTML = '';
    maximalLabelContainer.innerHTML = '';

    if (isLimitedDataType) {
        const minimalInput = document.createElement('input');
        minimalInput.type = 'number';
        minimalInput.id = `id_columns-${numberOfForm}-minimal`;
        minimalInput.name = `columns-${numberOfForm}-minimal`;
        minimalInput.setAttribute('class', 'form-control form-control-sm');

        const maximalInput = document.createElement('input');
        maximalInput.type = 'number';
        maximalInput.id = `id_columns-${numberOfForm}-maximal`;
        maximalInput.name = `columns-${numberOfForm}-maximal`;
        maximalInput.setAttribute('class', 'form-control form-control-sm');

        const minimalLabel = document.createElement('label');
        minimalLabel.setAttribute('for', `id_columns-${numberOfForm}-minimal`);
        minimalLabel.textContent = 'From';

        const maximalLabel = document.createElement('label');
        maximalLabel.setAttribute('for', `id_columns-${numberOfForm}-maximal`);
        maximalLabel.textContent = 'To';

        minimalInputContainer.appendChild(minimalInput);
        maximalInputContainer.appendChild(maximalInput);
        minimalLabelContainer.appendChild(minimalLabel);
        maximalLabelContainer.appendChild(maximalLabel);
    }
}

// Deletion of columns
for (let i = 0; i < totalForms.value; i++) {
    const deletionLink = document.querySelector(`.deletion-form-${i}-link a`);
    deletionLink.addEventListener('click', function (event) {
        event.preventDefault();
        markDeletionAndHide(i, deletionLink);
    });
}

function markDeletionAndHide(formNumber, link) {
    const inputElement = document.createElement('input');
    inputElement.type = 'checkbox';
    inputElement.id = `id_columns-${formNumber}-DELETE`;
    inputElement.name = `columns-${formNumber}-DELETE`;
    inputElement.setAttribute('checked', '');

    link.parentNode.appendChild(inputElement);

    link.parentNode.parentNode.parentNode.style.display = 'none';
}