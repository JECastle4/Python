import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import AstronomyScene from './AstronomyScene.vue';

// Mock Three.js modules to avoid WebGL context errors
vi.mock('@/three/scene', () => ({
  SceneManager: class MockSceneManager {
    scene = {};
    camera = {};
    renderer = {};
    controls = {};
    addObject = vi.fn();
    removeObject = vi.fn();
    render = vi.fn();
    setViewMode = vi.fn();
    resize = vi.fn();
    dispose = vi.fn();
    startAnimation = vi.fn();
    stopAnimation = vi.fn();
  },
}));

vi.mock('@/three/objects/Earth', () => ({
  Earth: class MockEarth {
    addToScene = vi.fn();
    update = vi.fn();
  },
}));

vi.mock('@/three/objects/Sun', () => ({
  Sun: class MockSun {
    addToScene = vi.fn();
    update = vi.fn();
  },
}));

vi.mock('@/three/objects/Moon', () => ({
  Moon: class MockMoon {
    addToScene = vi.fn();
    update = vi.fn();
  },
}));

vi.mock('@/composables/useAstronomyData', () => ({
  useAstronomyData: vi.fn(() => ({
    loading: { value: false },
    error: { value: null },
    data: { value: null },
    loadData: vi.fn(),
    hasData: { value: false },
  })),
}));

describe('AstronomyScene - Form Validation', () => {
  let wrapper: ReturnType<typeof mount>;

  beforeEach(() => {
    wrapper = mount(AstronomyScene);
  });

  describe('isLatitudeValid', () => {
    it('should accept valid latitude values at boundaries', () => {
      const vm = wrapper.vm as any;
      vm.params.latitude = -90;
      expect(vm.isLatitudeValid).toBe(true);
      vm.params.latitude = 0;
      expect(vm.isLatitudeValid).toBe(true);
      vm.params.latitude = 90;
      expect(vm.isLatitudeValid).toBe(true);
    });

    it('should reject latitude values below -90', () => {
      const vm = wrapper.vm as any;
      vm.params.latitude = -91;
      expect(vm.isLatitudeValid).toBe(false);
    });

    it('should reject latitude values above 90', () => {
      const vm = wrapper.vm as any;
      vm.params.latitude = 91;
      expect(vm.isLatitudeValid).toBe(false);
    });

    it('should reject NaN values (empty input)', () => {
      const vm = wrapper.vm as any;
      vm.params.latitude = NaN;
      expect(vm.isLatitudeValid).toBe(false);
    });

    it('should reject Infinity values', () => {
      const vm = wrapper.vm as any;
      vm.params.latitude = Infinity;
      expect(vm.isLatitudeValid).toBe(false);
    });
  });

  describe('isLongitudeValid', () => {
    it('should accept valid longitude values', () => {
      const testCases = [-180, -90, 0, 90, 180];
      
      for (const lon of testCases) {
        const vm = wrapper.vm as any;
        vm.params.longitude = lon;
        expect(vm.isLongitudeValid).toBe(true);
      }
    });

    it('should reject longitude values below -180', () => {
      const vm = wrapper.vm as any;
      vm.params.longitude = -181;
      expect(vm.isLongitudeValid).toBe(false);
    });

    it('should reject longitude values above 180', () => {
      const vm = wrapper.vm as any;
      vm.params.longitude = 181;
      expect(vm.isLongitudeValid).toBe(false);
    });

    it('should reject NaN values (empty input)', () => {
      const vm = wrapper.vm as any;
      vm.params.longitude = NaN;
      expect(vm.isLongitudeValid).toBe(false);
    });

    it('should reject Infinity values', () => {
      const vm = wrapper.vm as any;
      vm.params.longitude = -Infinity;
      expect(vm.isLongitudeValid).toBe(false);
    });
  });

  describe('isFrameCountValid', () => {
    it('should accept valid frame count values', () => {
      const testCases = [2, 10, 100, 500, 1000];
      
      for (const count of testCases) {
        const vm = wrapper.vm as any;
        vm.params.frame_count = count;
        expect(vm.isFrameCountValid).toBe(true);
      }
    });

    it('should reject frame count below 2', () => {
      const vm = wrapper.vm as any;
      vm.params.frame_count = 1;
      expect(vm.isFrameCountValid).toBe(false);
    });

    it('should reject frame count above 1000', () => {
      const vm = wrapper.vm as any;
      vm.params.frame_count = 1001;
      expect(vm.isFrameCountValid).toBe(false);
    });

    it('should reject non-integer values', () => {
      const vm = wrapper.vm as any;
      vm.params.frame_count = 10.5;
      expect(vm.isFrameCountValid).toBe(false);
    });

    it('should reject NaN values (empty input)', () => {
      const vm = wrapper.vm as any;
      vm.params.frame_count = NaN;
      expect(vm.isFrameCountValid).toBe(false);
    });

    it('should reject Infinity values', () => {
      const vm = wrapper.vm as any;
      vm.params.frame_count = Infinity;
      expect(vm.isFrameCountValid).toBe(false);
    });
  });

  describe('isFormValid', () => {
    it('should be true when all fields are valid', () => {
      const vm = wrapper.vm as any;
      vm.params.latitude = 51.5;
      vm.params.longitude = -0.1;
      vm.params.frame_count = 100;
      expect(vm.isFormValid).toBe(true);
    });

    it('should be false when latitude is invalid', () => {
      const vm = wrapper.vm as any;
      vm.params.latitude = 100;
      vm.params.longitude = -0.1;
      vm.params.frame_count = 100;
      expect(vm.isFormValid).toBe(false);
    });

    it('should be false when longitude is invalid', () => {
      const vm = wrapper.vm as any;
      vm.params.latitude = 51.5;
      vm.params.longitude = 200;
      vm.params.frame_count = 100;
      expect(vm.isFormValid).toBe(false);
    });

    it('should be false when frame count is invalid', () => {
      const vm = wrapper.vm as any;
      vm.params.latitude = 51.5;
      vm.params.longitude = -0.1;
      vm.params.frame_count = 1;
      expect(vm.isFormValid).toBe(false);
    });

    it('should be false when any field is NaN', () => {
      const vm = wrapper.vm as any;
      vm.params.latitude = NaN;
      vm.params.longitude = -0.1;
      vm.params.frame_count = 100;
      expect(vm.isFormValid).toBe(false);
    });
  });

  describe('Button disabled state', () => {
    it('should have disabled property when form is invalid', async () => {
      const vm = wrapper.vm as any;
      vm.params.latitude = 100; // Invalid
      await wrapper.vm.$nextTick();
      
      expect(vm.isFormValid).toBe(false);
    });

    it('should not have disabled property when form is valid', async () => {
      const vm = wrapper.vm as any;
      vm.params.latitude = 51.5;
      vm.params.longitude = -0.1;
      vm.params.frame_count = 100;
      await wrapper.vm.$nextTick();
      
      expect(vm.isFormValid).toBe(true);
    });
  });
});
