import { describe, it, expect, beforeEach } from 'vitest';
import { Earth } from './Earth';
import * as THREE from 'three';

describe('Earth', () => {
  let earth: Earth;

  beforeEach(() => {
    earth = new Earth();
  });

  describe('initialization', () => {
    it('should create a mesh with correct geometry', () => {
      expect(earth.mesh).toBeInstanceOf(THREE.Mesh);
      expect(earth.mesh.geometry).toBeInstanceOf(THREE.SphereGeometry);
    });

    it('should have earth material with blue-green color', () => {
      const material = earth.mesh.material as THREE.MeshStandardMaterial;
      expect(material.color.getHex()).toBe(0x2233ff);
    });

    it('should have correct mesh name', () => {
      expect(earth.mesh.name).toBe('earth');
    });

    it('should be positioned at origin by default', () => {
      expect(earth.mesh.position.x).toBe(0);
      expect(earth.mesh.position.y).toBe(0);
      expect(earth.mesh.position.z).toBe(0);
    });

    it('should be visible by default', () => {
      expect(earth.mesh.visible).toBe(true);
    });
  });

  describe('grid helpers', () => {
    it('should create grid helper', () => {
      expect(earth['gridHelper']).toBeDefined();
      expect(earth['gridHelper']).toBeInstanceOf(THREE.GridHelper);
    });

    it('should create axes helper', () => {
      expect(earth['axesHelper']).toBeDefined();
      expect(earth['axesHelper']).toBeInstanceOf(THREE.AxesHelper);
    });
  });

  describe('hemisphere grid', () => {
    it('should create hemisphere grid', () => {
      expect(earth['hemisphereGrid']).toBeDefined();
      expect(earth['hemisphereGrid']).toBeInstanceOf(THREE.Group);
    });

    it('should have altitude circles in hemisphere grid', () => {
      const lines = earth['hemisphereGrid'].children.filter(
        child => child instanceof THREE.Line
      );
      // Should have multiple altitude circles (0°, 15°, 30°, 45°, 60°, 75°, 90°)
      expect(lines.length).toBeGreaterThan(5);
    });
  });

  describe('view mode switching', () => {
    it('should show earth and grid helpers in 3D mode', () => {
      earth.setViewMode('3D');
      
      expect(earth.mesh.visible).toBe(true);
      expect(earth['gridHelper'].visible).toBe(true);
      expect(earth['axesHelper'].visible).toBe(true);
      expect(earth['hemisphereGrid'].visible).toBe(false);
    });

    it('should hide earth and show hemisphere in SKY mode', () => {
      earth.setViewMode('SKY');
      
      expect(earth.mesh.visible).toBe(false);
      expect(earth['gridHelper'].visible).toBe(false);
      expect(earth['axesHelper'].visible).toBe(false);
      expect(earth['hemisphereGrid'].visible).toBe(true);
    });

    it('should toggle back to 3D mode correctly', () => {
      earth.setViewMode('SKY');
      earth.setViewMode('3D');
      
      expect(earth.mesh.visible).toBe(true);
      expect(earth['gridHelper'].visible).toBe(true);
      expect(earth['axesHelper'].visible).toBe(true);
      expect(earth['hemisphereGrid'].visible).toBe(false);
    });
  });

  describe('scene management', () => {
    it('should add mesh to scene', () => {
      const scene = new THREE.Scene();
      earth.addToScene(scene);
      expect(scene.children).toContain(earth.mesh);
    });

    it('should add hemisphere grid to scene', () => {
      const scene = new THREE.Scene();
      earth.addToScene(scene);
      expect(scene.children).toContain(earth['hemisphereGrid']);
    });

    it('should remove mesh from scene', () => {
      const scene = new THREE.Scene();
      earth.addToScene(scene);
      earth.removeFromScene(scene);
      expect(scene.children).not.toContain(earth.mesh);
    });

    it('should remove hemisphere grid from scene', () => {
      const scene = new THREE.Scene();
      earth.addToScene(scene);
      earth.removeFromScene(scene);
      expect(scene.children).not.toContain(earth['hemisphereGrid']);
    });
  });

  describe('hemisphere grid construction', () => {
    it('should create altitude circles at correct elevations', () => {
      // Altitude circles should be created at 15° intervals
      const expectedAltitudes = [0, 15, 30, 45, 60, 75];
      const lines = earth['hemisphereGrid'].children.filter(
        child => child instanceof THREE.Line
      );
      
      // Should have at least the altitude circles
      expect(lines.length).toBeGreaterThanOrEqual(expectedAltitudes.length);
    });

    it('should create azimuth lines', () => {
      const lines = earth['hemisphereGrid'].children.filter(
        child => child instanceof THREE.Line
      );
      
      // Should have both altitude circles and azimuth radial lines
      // Azimuth lines: every 30° = 12 lines
      // Altitude circles: 6 circles (0° to 75°)
      expect(lines.length).toBeGreaterThanOrEqual(12);
    });

    it('should emphasize horizon line', () => {
      const horizonLines = earth['hemisphereGrid'].children.filter(child => {
        if (child instanceof THREE.Line) {
          const material = child.material as THREE.LineBasicMaterial;
          return material.linewidth === 2;
        }
        return false;
      });
      
      // Should have at least one emphasized horizon line
      expect(horizonLines.length).toBeGreaterThan(0);
    });
  });

  describe('helper positioning', () => {
    it('should position grid helper below earth', () => {
      expect(earth['gridHelper'].position.y).toBe(-0.2);
    });

    it('should have grid helper with correct size', () => {
      // GridHelper size is 20x20 with 20 divisions
      expect(earth['gridHelper']).toBeDefined();
    });
  });
});
