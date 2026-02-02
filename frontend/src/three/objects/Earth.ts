import * as THREE from 'three';

/**
 * Earth (observer) representation at origin
 */
export class Earth {
  public mesh: THREE.Mesh;
  private gridHelper: THREE.GridHelper;
  private axesHelper: THREE.AxesHelper;

  constructor() {
    // Create small earth at origin (observer position)
    const geometry = new THREE.SphereGeometry(0.2, 32, 32);
    const material = new THREE.MeshStandardMaterial({
      color: 0x2233ff,
      roughness: 0.7,
      metalness: 0.3,
    });

    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.name = 'earth';

    // Add grid helper to show ground plane
    this.gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x222222);
    this.gridHelper.position.y = -0.2;

    // Add axes helper for orientation
    this.axesHelper = new THREE.AxesHelper(2);
  }

  public addToScene(scene: THREE.Scene): void {
    scene.add(this.mesh);
    scene.add(this.gridHelper);
    scene.add(this.axesHelper);
  }

  public removeFromScene(scene: THREE.Scene): void {
    scene.remove(this.mesh);
    scene.remove(this.gridHelper);
    scene.remove(this.axesHelper);
  }
}
