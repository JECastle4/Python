import * as THREE from 'three';

/**
 * Moon object for the scene
 */
export class Moon {
  public mesh: THREE.Mesh;

  constructor() {
    // Create moon geometry
    const geometry = new THREE.SphereGeometry(0.3, 32, 32);
    const material = new THREE.MeshStandardMaterial({
      color: 0xcccccc,
      roughness: 0.9,
      metalness: 0.1,
    });

    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.name = 'moon';
  }

  /**
   * Update moon position based on spherical coordinates
   */
  public updatePosition(azimuth: number, altitude: number, isVisible: boolean = true): void {
    // Convert azimuth/altitude to Three.js coordinates
    const azimuthRad = THREE.MathUtils.degToRad(azimuth);
    const altitudeRad = THREE.MathUtils.degToRad(altitude);

    // Use fixed distance for visualization
    const distance = 8;

    this.mesh.position.x = distance * Math.cos(altitudeRad) * Math.sin(azimuthRad);
    this.mesh.position.y = distance * Math.sin(altitudeRad);
    this.mesh.position.z = -distance * Math.cos(altitudeRad) * Math.cos(azimuthRad);
    
    // Update visibility
    this.mesh.visible = isVisible;
  }

  /**
   * Update moon phase appearance
   */
  public updatePhase(illumination: number): void {
    // Adjust brightness based on phase
    const material = this.mesh.material as THREE.MeshStandardMaterial;
    material.emissive = new THREE.Color(0x444444);
    material.emissiveIntensity = illumination / 100;
  }

  public addToScene(scene: THREE.Scene): void {
    scene.add(this.mesh);
  }

  public removeFromScene(scene: THREE.Scene): void {
    scene.remove(this.mesh);
  }
}
