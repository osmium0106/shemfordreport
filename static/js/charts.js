// Simple Chart Creation Functions
function createSimpleChart(canvasId, labels, data, subjectName) {
    console.log('Creating chart for:', canvasId);
    console.log('Labels:', labels);
    console.log('Data:', data);
    
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error('Canvas not found:', canvasId);
        return;
    }
    
    // Get the container dimensions
    const container = canvas.parentElement;
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    
    // Set canvas size to fill container
    canvas.width = containerWidth;
    canvas.height = containerHeight;
    canvas.style.width = containerWidth + 'px';
    canvas.style.height = containerHeight + 'px';
    
    const ctx = canvas.getContext('2d');
    
    // Clear the canvas first
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Basic chart drawing with full dimensions
    try {
        // Chart dimensions - use more of the available space
        const padding = Math.min(containerWidth * 0.08, 50); // Responsive padding
        const chartWidth = canvas.width - 2 * padding;
        const chartHeight = canvas.height - 2 * padding;
        
        // Find max value for scaling
        const maxValue = Math.max(...data, 12); // At least 12 for the scale
        
        // Set up responsive font sizes
        const titleFontSize = Math.max(14, containerWidth * 0.025);
        const labelFontSize = Math.max(10, containerWidth * 0.018);
        const valueFontSize = Math.max(12, containerWidth * 0.02);
        
        // Draw background
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw axes
        ctx.strokeStyle = '#666';
        ctx.lineWidth = 2;
        
        // Y-axis
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, padding + chartHeight);
        ctx.stroke();
        
        // X-axis
        ctx.beginPath();
        ctx.moveTo(padding, padding + chartHeight);
        ctx.lineTo(padding + chartWidth, padding + chartHeight);
        ctx.stroke();
        
        // Draw Y-axis labels and grid lines
        ctx.fillStyle = '#666';
        ctx.font = `${labelFontSize}px Arial`;
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        
        for (let i = 0; i <= 12; i += 2) {
            const y = padding + chartHeight - (i / maxValue) * chartHeight;
            ctx.fillText(i.toString(), padding - 10, y);
            
            // Draw grid lines
            if (i > 0) {
                ctx.strokeStyle = '#f0f0f0';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(padding, y);
                ctx.lineTo(padding + chartWidth, y);
                ctx.stroke();
            }
        }
        
        // Y-axis title
        ctx.save();
        ctx.translate(20, padding + chartHeight / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillStyle = '#333';
        ctx.font = `bold ${labelFontSize}px Arial`;
        ctx.textAlign = 'center';
        ctx.fillText('Marks', 0, 0);
        ctx.restore();
        
        // Draw data if available
        if (data.length > 0 && labels.length > 0) {
            const stepX = chartWidth / Math.max(labels.length - 1, 1);
            
            // Draw target line at 9 marks first (behind data)
            const targetY = padding + chartHeight - (9 / maxValue) * chartHeight;
            ctx.strokeStyle = '#28a745';
            ctx.lineWidth = 2;
            ctx.setLineDash([8, 4]);
            ctx.beginPath();
            ctx.moveTo(padding, targetY);
            ctx.lineTo(padding + chartWidth, targetY);
            ctx.stroke();
            ctx.setLineDash([]);
            
            // Target label
            ctx.fillStyle = '#28a745';
            ctx.font = `${labelFontSize}px Arial`;
            ctx.textAlign = 'left';
            ctx.textBaseline = 'bottom';
            ctx.fillText('Target (9 marks)', padding + 10, targetY - 5);
            
            // Draw area under the line
            ctx.fillStyle = 'rgba(0, 123, 255, 0.1)';
            ctx.beginPath();
            ctx.moveTo(padding, padding + chartHeight);
            for (let i = 0; i < data.length; i++) {
                const x = padding + i * stepX;
                const y = padding + chartHeight - (data[i] / maxValue) * chartHeight;
                if (i === 0) {
                    ctx.lineTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.lineTo(padding + (data.length - 1) * stepX, padding + chartHeight);
            ctx.closePath();
            ctx.fill();
            
            // Draw main line
            ctx.strokeStyle = '#007bff';
            ctx.lineWidth = 3;
            ctx.beginPath();
            
            for (let i = 0; i < data.length; i++) {
                const x = padding + i * stepX;
                const y = padding + chartHeight - (data[i] / maxValue) * chartHeight;
                
                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.stroke();
            
            // Draw points and labels
            for (let i = 0; i < data.length; i++) {
                const x = padding + i * stepX;
                const y = padding + chartHeight - (data[i] / maxValue) * chartHeight;
                
                // Point color based on value
                if (data[i] >= 9) {
                    ctx.fillStyle = '#28a745'; // Green for good performance
                } else if (data[i] >= 6) {
                    ctx.fillStyle = '#ffc107'; // Yellow for average
                } else {
                    ctx.fillStyle = '#dc3545'; // Red for needs improvement
                }
                
                // Draw point shadow
                ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
                ctx.beginPath();
                ctx.arc(x + 1, y + 1, 8, 0, 2 * Math.PI);
                ctx.fill();
                
                // Draw main point
                if (data[i] >= 9) {
                    ctx.fillStyle = '#28a745';
                } else if (data[i] >= 6) {
                    ctx.fillStyle = '#ffc107';
                } else {
                    ctx.fillStyle = '#dc3545';
                }
                
                ctx.beginPath();
                ctx.arc(x, y, 8, 0, 2 * Math.PI);
                ctx.fill();
                
                // White border on point
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 3;
                ctx.stroke();
                
                // Value above point
                ctx.fillStyle = '#333';
                ctx.font = `bold ${valueFontSize}px Arial`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';
                ctx.fillText(data[i].toString(), x, y - 15);
                
                // X-axis labels
                ctx.fillStyle = '#666';
                ctx.font = `${labelFontSize}px Arial`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'top';
                
                // Rotate labels if they're too long
                ctx.save();
                if (labels[i].length > 8) {
                    ctx.translate(x, padding + chartHeight + 15);
                    ctx.rotate(-Math.PI / 4);
                    ctx.fillText(labels[i], 0, 0);
                } else {
                    ctx.fillText(labels[i], x, padding + chartHeight + 15);
                }
                ctx.restore();
            }
        }
        
        // Chart title
        ctx.fillStyle = '#333';
        ctx.font = `bold ${titleFontSize}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillText(subjectName + ' Progress Chart', canvas.width / 2, 10);
        
        // Legend
        const legendY = canvas.height - 30;
        const legendItems = [
            { color: '#007bff', label: 'Score Line' },
            { color: '#28a745', label: 'Target (9 marks)' }
        ];
        
        let legendX = canvas.width / 2 - 80;
        legendItems.forEach((item, index) => {
            // Legend color box
            ctx.fillStyle = item.color;
            ctx.fillRect(legendX, legendY, 12, 12);
            
            // Legend text
            ctx.fillStyle = '#666';
            ctx.font = `${labelFontSize}px Arial`;
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText(item.label, legendX + 18, legendY + 6);
            
            legendX += item.label.length * 8 + 40;
        });
        
        console.log('Chart created successfully for:', subjectName);
        
        // Hide loading message
        const loadingMsg = document.getElementById(canvasId.replace('ProgressChart', 'LoadingMessage'));
        if (loadingMsg) {
            loadingMsg.style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error drawing chart:', error);
        
        // Show error message
        ctx.fillStyle = '#dc3545';
        ctx.font = `${titleFontSize}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('Error loading chart', canvas.width / 2, canvas.height / 2);
    }
}

// Function to initialize all charts
function initializeAllCharts() {
    console.log('Initializing all charts with simple drawing...');
    
    // This will be populated by the template
    window.chartData = window.chartData || {};
    
    Object.keys(window.chartData).forEach(subjectName => {
        const data = window.chartData[subjectName];
        const canvasId = subjectName.toLowerCase() + 'ProgressChart';
        createSimpleChart(canvasId, data.labels, data.values, subjectName);
    });
}