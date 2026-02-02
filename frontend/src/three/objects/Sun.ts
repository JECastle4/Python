import * as THREE from 'three';

/**
 * Sun object for the scene
 */
export class Sun {
  public mesh: THREE.Mesh;
  private light: THREE.PointLight;

  constructor() {
    // Create sun geometry
    const geometry = new THREE.SphereGeometry(0.5, 32, 32);
    const material = new THREE.MeshBasicMaterial({
      color: 0xffaa00,
      emissive: 0xffaa00,
      emissiveIntensity: 1.0,
    });

    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.name = 'sun';

    // Add point light at sun position
    this.light = new THREE.PointLight(0xffffdd, 2.0, 100);
    this.mesh.add(this.light);
  }

  /**
   * Update sun position based on spherical coordinates
   */
  public updatePosition(azimuth: number, altitude: number, isVisible: boolean = true): void {
    // Convert azimuth/altitude to Three.js coordinates
    // Azimuth: 0° = North, 90° = East (clockwise from above)
    // Altitude: 0° = horizon, 90° = zenith
    
    const azimuthRad = THREE.MathUtils.degToRad(azimuth);
    const altitudeRad = THREE.MathUtils.degToRad(altitude);

    // Use fixed distance for visualization
    const distance = 15;

    this.mesh.position.x = distance * Math.cos(altitudeRad) * Math.sin(azimuthRad);
    this.mesh.position.y = distance * Math.sin(altitudeRad);
    this.mesh.position.z = -distance * Math.cos(altitudeRad) * Math.cos(azimuthRad);
    
    // Update visibility
    this.mesh.visible = isVisible;
    this.light.visible = isVisible;
  }

  public addToScene(scene: THREE.Scene): void {
    scene.add(this.mesh);
  }

  public removeFromScene(scene: THREE.Scene): void {
    scene.remove(this.mesh);
  }
}
