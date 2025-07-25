// static/js/dashboard.js

$(function() {
    // Função para obter o CSRF token do cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Função para enviar atualização de status via AJAX (Kanban)
    function updateLeadStatus(leadId, newStatus) {
        const csrftoken = getCookie('csrftoken');

        $.ajax({
            url: '/dashboard/leads/update-status-kanban/',
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
                // Você pode adicionar um feedback visual mais amigável aqui, se quiser
            },
            error: function(xhr, status, error) {
                console.error("Erro ao atualizar status:", xhr.responseText);
                alert("Erro ao atualizar status do lead: " + (xhr.responseJSON ? xhr.responseJSON.message : "Erro desconhecido"));
                location.reload(); // Recarrega para reverter o estado visual em caso de erro
            }
        });
    }

    // Configura o arrastar e soltar para os cards Kanban
    $(".kanban-cards").sortable({
        connectWith: ".kanban-cards",
        placeholder: "ui-sortable-placeholder",
        cursor: "grabbing",
        items: ".kanban-card",
        receive: function(event, ui) {
            var leadId = ui.item.data('lead-id');
            var newStatus = $(this).data('status');
            console.log("Card " + leadId + " movido para o status: " + newStatus);
            updateLeadStatus(leadId, newStatus);
        }
    }).disableSelection();

    // Lógica para renderizar os gráficos Chart.js
    // Garante que o script só execute se o canvas existir (ou seja, na página do Dashboard Admin/Gerente)
    if (document.getElementById('salesTrendChart') && typeof Chart !== 'undefined') {
        const salesCtx = document.getElementById('salesTrendChart').getContext('2d');
        const conversionCtx = document.getElementById('conversionRateChart').getContext('2d');

        // Certifique-se de que as variáveis salesTrendLabels, salesTrendData, etc.
        // são definidas no HTML ANTES deste script ser carregado.
        // Elas vêm do contexto do Django, como:
        // const salesTrendLabels = {{ sales_trend_labels|safe }};

        // Gráfico de Tendência de Vendas
        new Chart(salesCtx, {
            type: 'line',
            data: {
                labels: salesTrendLabels, // Parseia a string JSON para um array JS
                datasets: [{
                    label: 'Receita (R$)',
                    data: salesTrendData, // Parseia a string JSON para um array JS
                    borderColor: 'rgb(234, 0, 30)', // var(--bs-primary)
                    backgroundColor: 'rgba(234, 0, 30, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Receita (R$)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Mês'
                        }
                    }
                }
            }
        });

        // Gráfico de Taxa de Conversão
        new Chart(conversionCtx, {
            type: 'line',
            data: {
                labels: conversionTrendLabels, // Parseia a string JSON para um array JS
                datasets: [{
                    label: 'Taxa de Conversão (%)',
                    data: conversionTrendData, // Parseia a string JSON para um array JS
                    borderColor: 'rgb(31, 46, 78)', // var(--bs-secondary)
                    backgroundColor: 'rgba(31, 46, 78, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Taxa de Conversão (%)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Mês'
                        }
                    }
                }
            }
        });
    }
});
