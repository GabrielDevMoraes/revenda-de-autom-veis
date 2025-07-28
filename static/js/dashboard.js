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
                        display: false,
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
// ... (seu código existente Chart.js e Kanban) ...

    // Lógica para carregar e renderizar gráficos do modal de Análise Rápida
    $('#quickAnalysisModal').on('shown.bs.modal', function () {
        $.ajax({
            url: '/dashboard/admin/quick-analysis-data/', // URL da sua nova view
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                // Gráfico de Carros por Status (Gráfico de Barras)
                const carsCtx = document.getElementById('carsByStatusChart').getContext('2d');
                new Chart(carsCtx, {
                    type: 'bar', // Pode ser 'pie' ou 'doughnut' também
                    data: {
                        labels: data.carsByStatusLabels,
                        datasets: [{
                            label: 'Número de Carros',
                            data: data.carsByStatusData,
                            backgroundColor: [
                                'rgba(234, 0, 30, 0.7)', // Cor para Disponível
                                'rgba(31, 46, 78, 0.7)', // Cor para Vendido
                                'rgba(255, 159, 64, 0.7)', // Cor para Manutenção
                                'rgba(75, 192, 192, 0.7)', // Adicione mais cores conforme seus status
                            ],
                            borderColor: [
                                'rgb(234, 0, 30)',
                                'rgb(31, 46, 78)',
                                'rgb(255, 159, 64)',
                                'rgb(75, 192, 192)',
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'bottom', // Ou 'bottom', dependendo do que fica melhor no seu layout
                                labels: {
                                    // Esta função personaliza o que aparece na legenda
                                    generateLabels: function(chart) {
                                        const dataset = chart.data.datasets[0]; // Assume que você tem apenas um dataset
                                        return chart.data.labels.map((label, i) => {
                                            const backgroundColor = dataset.backgroundColor[i];
                                            return {
                                                text: label, // O texto da legenda será o nome do status (label do data.labels)
                                                fillStyle: backgroundColor, // A cor será a cor do background da barra
                                                strokeStyle: backgroundColor,
                                                lineWidth: 1,
                                                // hidden: chart.isDatasetVisible(0) ? false : true, // Para permitir esconder/mostrar clicando
                                                // hidden: !chart.isDatasetVisible(0) || !chart.getDatasetMeta(0).data[i].hidden, // Permite clicar para ocultar
                                                hidden: !chart.isDatasetVisible(0) || chart.getDatasetMeta(0).data[i].hidden,
                                                // Essas duas propriedades são importantes para que o clique na legenda funcione:
                                                datasetIndex: 0, // Indica qual dataset este item de legenda pertence
                                                index: i // O índice do dado (barra) ao qual este item de legenda corresponde
                                            };
                                        });
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    precision: 0
                                }
                            }
                        }
                    }
                });

                // Gráfico de Leads por Status (Gráfico de Rosca/Doughnut)
                const leadsCtx = document.getElementById('leadsByStatusChart').getContext('2d');
                new Chart(leadsCtx, {
                    type: 'doughnut', // Pode ser 'pie' ou 'bar' também
                    data: {
                        labels: data.leadsByStatusLabels,
                        datasets: [{
                            label: 'Número de Leads',
                            data: data.leadsByStatusData,
                            backgroundColor: [
                                'rgba(54, 162, 235, 0.7)', // Cor para Novo
                                'rgba(255, 206, 86, 0.7)', // Cor para Contatado
                                'rgba(153, 102, 255, 0.7)', // Cor para Negociação
                                'rgba(255, 99, 132, 0.7)', // Cor para Finalizado
                                // Adicione mais cores conforme seus status
                            ],
                            borderColor: [
                                'rgb(54, 162, 235)',
                                'rgb(255, 206, 86)',
                                'rgb(153, 102, 255)',
                                'rgb(255, 99, 132)',
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'right'
                            }
                        }
                    }
                });
            },
            error: function(xhr, status, error) {
                console.error("Erro ao carregar dados de análise rápida:", xhr.responseText);
                alert("Não foi possível carregar os dados de análise rápida. Tente novamente.");
            }
        });
    });
