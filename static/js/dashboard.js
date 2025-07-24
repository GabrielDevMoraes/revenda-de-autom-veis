// static/js/dashboard.js

$(function() {
    // Configura o arrastar e soltar para os cards
    $(".kanban-cards").sortable({
        connectWith: ".kanban-cards", // Permite mover entre diferentes listas
        placeholder: "ui-sortable-placeholder", // Estilo do placeholder
        cursor: "grabbing", // Cursor ao arrastar
        items: ".kanban-card", // Quais elementos são arrastáveis
        receive: function(event, ui) {
            // Quando um card é recebido em uma nova coluna
            var leadId = ui.item.data('lead-id');
            var newStatus = $(this).data('status'); // Pega o status da coluna de destino

            console.log("Card " + leadId + " movido para o status: " + newStatus);

            // Envia a atualização para o servidor via AJAX
            updateLeadStatus(leadId, newStatus);
        }
    }).disableSelection(); // Desabilita a seleção de texto ao arrastar

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function updateLeadStatus(leadId, newStatus) {
        const csrftoken = getCookie('csrftoken');

        $.ajax({
            url: '/dashboard/leads/update-status-kanban/', // URL da sua view Django para atualizar status
            type: 'POST',
            data: JSON.stringify({
                'lead_id': leadId,
                'new_status': newStatus
            }),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function(response) {
                console.log("Sucesso na atualização do status:", response.message);
                // Opcional: Mostrar uma mensagem de sucesso na tela (usando Django messages ou um toast)
                // Se você quiser que as mensagens do Django apareçam, pode precisar de um refresh ou de um mecanismo AJAX para buscá-las.
                // Por agora, o console.log e o status do lead no card já são um feedback.
            },
            error: function(xhr, status, error) {
                console.error("Erro ao atualizar status:", xhr.responseText);
                // Opcional: Reverter o card para a posição original ou mostrar uma mensagem de erro
                alert("Erro ao atualizar status do lead: " + (xhr.responseJSON ? xhr.responseJSON.message : "Erro desconhecido"));
                // Recarrega a página para reverter o estado visual em caso de erro
                location.reload(); 
            }
        });
    }
});
