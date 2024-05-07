function runBreadthFirstLayout(){
    var layout = cy.layout({
        name: 'breadthfirst',
        directed: true
    });
    layout.run();
}

function defineNodeStyle() {
    // Define node style
    cy.style()
        .selector('node')
        .style(
        {
            'label': 'data(label)', 'background-color': function(ele) {return ele.data('color');}
        });
    cy.style().update();
}

function defineEdgeStyleMultipleHttpBlocks(){
    cy.style()
        .selector('edge')
        .style({
            'label': 'data(weight)', // This maps the 'label' property in edge data to the label text
            'curve-style': 'bezier', // Ensures smooth curved lines for directed edges
            'target-arrow-shape': 'triangle', // Adds an arrowhead at the target end of the edge
            'line-color': 'data(color)', // Use the 'color' data property for the edge color
            'target-arrow-color': 'data(color)', // Optionally, also set the arrow color
            'line-opacity':'data(opacity)'
            // 'line-color': (ele) => {
            //     const edgeData = ele.data();
            //     const statusCode = edgeData.status_code;
            //     if (statusCode == 100)
            //         return 'lightblue';
            //     else if(statusCode == 200)
            //         return 'green';    
            //     else if(statusCode == 300)
            //         return 'yellow';
            //     else if(statusCode == 400)
            //         return 'orange';
            //     else if(statusCode == 500)
            //         return 'red';
            //     else
            //         return 'black'
            // }
        })
    cy.style().update();    
}