function createSkillsGraph(skills) {
    const graphGeometry = new THREE.BufferGeometry();
    const positions = [];
    const colors = [];
    
    skills.forEach((skill, i) => {
        const angle = (i / skills.length) * Math.PI * 2;
        const radius = 1;
        positions.push(
            Math.cos(angle) * radius,
            Math.sin(angle) * radius,
            0
        );
        colors.push(0, 0.8, 1);
    });
    
    graphGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    graphGeometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    
    return new THREE.Points(graphGeometry, new THREE.PointsMaterial({
        size: 0.1,
        vertexColors: true
    }));
} 