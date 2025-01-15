function createSuccessAnimation() {
    const particles = new THREE.Group();
    for(let i = 0; i < 50; i++) {
        const geometry = new THREE.SphereGeometry(0.02);
        const material = new THREE.MeshBasicMaterial({
            color: new THREE.Color(0x00ff87),
            transparent: true
        });
        const particle = new THREE.Mesh(geometry, material);
        particles.add(particle);
    }
    return particles;
} 