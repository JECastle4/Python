import { describe, it, expect, beforeEach } from 'vitest';
import { Moon } from './Moon';
import * as THREE from 'three';

describe('Moon', () => {
  let moon: Moon;

  beforeEach(() => {
    moon = new Moon();
  });

  describe('initialization', () => {
    it('should create a mesh with correct geometry', () => {
      expect(moon.mesh).toBeInstanceOf(THREE.Mesh);
      expect(moon.mesh.geometry).toBeInstanceOf(THREE.SphereGeometry);
    });

    it('should have moon material properties', () => {
      const material = moon.mesh.material as THREE.MeshStandardMaterial;
      expect(material.color.getHex()).toBe(0xcccccc);
      expect(material.roughness).toBe(0.9);
      expect(material.metalness).toBe(0.1);
    });

    it('should have correct mesh name', () => {
      expect(moon.mesh.name).toBe('moon');
    });

    it('should be visible by default', () => {
      expect(moon.mesh.visible).toBe(true);
    });

    it('should have standard material', () => {
      const material = moon.mesh.material as THREE.MeshStandardMaterial;
      expect(material).toBeInstanceOf(THREE.MeshStandardMaterial);
    });
  });

  describe('3D view positioning', () => {
    it('should position at zenith (altitude 90°)', () => {
      moon.updatePosition(0, 90, true, '3D');
      
      expect(moon.mesh.position.y).toBeCloseTo(8, 1);
      expect(Math.abs(moon.mesh.position.x)).toBeLessThan(0.1);
      expect(Math.abs(moon.mesh.position.z)).toBeLessThan(0.1);
    });

    it('should position at horizon north (azimuth 0°, altitude 0°)', () => {
      moon.updatePosition(0, 0, true, '3D');
      
      expect(Math.abs(moon.mesh.position.x)).toBeLessThan(0.1);
      expect(Math.abs(moon.mesh.position.y)).toBeLessThan(0.1);
      expect(moon.mesh.position.z).toBeCloseTo(-8, 1);
    });

    it('should position at horizon east (azimuth 90°, altitude 0°)', () => {
      moon.updatePosition(90, 0, true, '3D');
      
      expect(moon.mesh.position.x).toBeCloseTo(8, 1);
      expect(Math.abs(moon.mesh.position.y)).toBeLessThan(0.1);
      expect(Math.abs(moon.mesh.position.z)).toBeLessThan(0.1);
    });

    it('should use distance of 8 units in 3D view', () => {
      moon.updatePosition(45, 45, true, '3D');
      
      const distance = Math.sqrt(
        moon.mesh.position.x ** 2 +
        moon.mesh.position.y ** 2 +
        moon.mesh.position.z ** 2
      );
      expect(distance).toBeCloseTo(8, 1);
    });
  });

  describe('SKY view positioning', () => {
    it('should position at zenith on hemisphere', () => {
      moon.updatePosition(0, 90, true, 'SKY');
      
      expect(Math.abs(moon.mesh.position.x)).toBeLessThan(0.1);
      expect(moon.mesh.position.y).toBeCloseTo(10, 1);
      expect(Math.abs(moon.mesh.position.z)).toBeLessThan(0.1);
    });

    it('should position on horizon circle when altitude is 0°', () => {
      moon.updatePosition(0, 0, true, 'SKY');
      
      expect(moon.mesh.position.y).toBeCloseTo(0, 1);
      const horizontalDist = Math.sqrt(
        moon.mesh.position.x ** 2 + moon.mesh.position.z ** 2
      );
      expect(horizontalDist).toBeCloseTo(10, 1);
    });

    it('should position below horizon when altitude is negative', () => {
      moon.updatePosition(180, -15, true, 'SKY');
      
      expect(moon.mesh.position.y).toBe(0);
    });

    it('should use radius of 10 units in SKY view', () => {
      moon.updatePosition(0, 45, true, 'SKY');
      
      // Calculate distance from origin (should be on hemisphere of radius 10)
      const distance = Math.sqrt(
        moon.mesh.position.x ** 2 +
        moon.mesh.position.y ** 2 +
        moon.mesh.position.z ** 2
      );
      expect(distance).toBeCloseTo(10, 1);
    });
  });

  describe('phase illumination', () => {
    it('should update emissive intensity based on phase', () => {
      const material = moon.mesh.material as THREE.MeshStandardMaterial;
      
      // Full moon (100% illumination)
      moon.updatePhase(100);
      expect(material.emissiveIntensity).toBe(1.0);
      expect(material.emissive.getHex()).toBe(0x444444);
    });

    it('should have zero intensity for new moon', () => {
      const material = moon.mesh.material as THREE.MeshStandardMaterial;
      
      // New moon (0% illumination)
      moon.updatePhase(0);
      expect(material.emissiveIntensity).toBe(0);
    });

    it('should have medium intensity for half moon', () => {
      const material = moon.mesh.material as THREE.MeshStandardMaterial;
      
      // Half moon (50% illumination)
      moon.updatePhase(50);
      expect(material.emissiveIntensity).toBe(0.5);
    });

    it('should scale intensity correctly', () => {
      const material = moon.mesh.material as THREE.MeshStandardMaterial;
      
      // Test various illumination values (0-100 scale)
      const testValues = [0, 25, 50, 75, 100];
      testValues.forEach(illumination => {
        moon.updatePhase(illumination);
        expect(material.emissiveIntensity).toBe(illumination / 100);
      });
    });
  });

  describe('visibility control', () => {
    it('should hide mesh when isVisible is false', () => {
      moon.updatePosition(0, 45, false, '3D');
      expect(moon.mesh.visible).toBe(false);
    });

    it('should show mesh when isVisible is true', () => {
      moon.updatePosition(0, 45, true, '3D');
      expect(moon.mesh.visible).toBe(true);
    });
  });

  describe('scene management', () => {
    it('should add mesh to scene', () => {
      const scene = new THREE.Scene();
      moon.addToScene(scene);
      expect(scene.children).toContain(moon.mesh);
    });

    it('should remove mesh from scene', () => {
      const scene = new THREE.Scene();
      moon.addToScene(scene);
      moon.removeFromScene(scene);
      expect(scene.children).not.toContain(moon.mesh);
    });
  });
});
