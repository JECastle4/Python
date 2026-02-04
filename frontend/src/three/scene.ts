import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

/**
 * Three.js Scene Manager for Astronomy Animation
 */
export class SceneManager {
  public scene: THREE.Scene;
  public camera: THREE.PerspectiveCamera;
  public renderer: THREE.WebGLRenderer;
  public controls: OrbitControls;
  
  private animationId: number | null = null;
  private animationCallback?: () => void;
  private currentViewMode: '3D' | 'SKY' = '3D';
  private resizeHandler: () => void;

  constructor(canvas: HTMLCanvasElement) {
    // Create scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x000011);

    // Create camera
    this.camera = new THREE.PerspectiveCamera(
      75,
      canvas.clientWidth / canvas.clientHeight,
      0.1,
      1000
    );
    this.camera.position.set(0, 7, 14);

    // Create renderer
    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
    });
    this.renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Create controls
    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.minDistance = 2;
    this.controls.maxDistance = 50;

    // Add basic lighting
    this.setupLighting();

    // Handle window resize - store bound function to allow proper cleanup
    this.resizeHandler = this.onWindowResize.bind(this);
    window.addEventListener('resize', this.resizeHandler);
  }

  private setupLighting(): void {
    // Ambient light for general illumination
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
    this.scene.add(ambientLight);

    // Directional light from sun position (will be updated)
    const sunLight = new THREE.DirectionalLight(0xffffff, 1.0);
    sunLight.position.set(10, 0, 0);
    sunLight.name = 'sunLight';
    this.scene.add(sunLight);
  }

  private onWindowResize(): void {
    const canvas = this.renderer.domElement;
    this.camera.aspect = canvas.clientWidth / canvas.clientHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  }

  public startAnimation(callback?: () => void): void {
    this.animationCallback = callback;
    this.animate();
  }

  public stopAnimation(): void {
    if (this.animationId !== null) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  private animate(): void {
    this.animationId = requestAnimationFrame(this.animate.bind(this));

    // Update controls
    this.controls.update();

    // Call custom animation callback
    if (this.animationCallback) {
      this.animationCallback();
    }

    // Render scene
    this.renderer.render(this.scene, this.camera);
  }
  
  public setViewMode(mode: '3D' | 'SKY'): void {
    this.currentViewMode = mode;
    
    if (mode === '3D') {
      // 3D orbital view
      this.camera.position.set(0, 7, 14);
      this.controls.target.set(0, 0, 0);
      this.controls.minDistance = 2;
      this.controls.maxDistance = 50;
      this.scene.background = new THREE.Color(0x000011);
    } else {
      // Sky view: camera at ground level looking straight up
      // TODO (#26): Sky view zoom default not applying correctly when toggling views
      // Camera position should reset to default zoom level on view switch
      // Set limits first
      this.controls.minDistance = 0.1;
      this.controls.maxDistance = 80;  // Allow zooming out much further
      // Position camera and target - distance between them determines the zoom level
      this.camera.position.set(0, 0.1, 0);
      this.controls.target.set(0, 35, 0);  // Starting point - user can zoom in/out
      this.controls.enablePan = true;
      this.scene.background = new THREE.Color(0x001133);
    }
    
    // Force controls to update with new limits and target
    this.controls.update();
  }
  
  public getViewMode(): '3D' | 'SKY' {
    return this.currentViewMode;
  }

  public dispose(): void {
    this.stopAnimation();
    window.removeEventListener('resize', this.resizeHandler);
    this.controls.dispose();
    this.renderer.dispose();
  }
}
