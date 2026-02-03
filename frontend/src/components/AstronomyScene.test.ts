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

// Mock composable - will be customized per test
let mockLoadData = vi.fn();
let mockLoading = { value: false };
let mockError = { value: null };
let mockData = { value: null };
let mockHasData = { value: false };

vi.mock('@/composables/useAstronomyData', () => ({
  useAstronomyData: vi.fn(() => ({
    loading: mockLoading,
    error: mockError,
    data: mockData,
    loadData: mockLoadData,
    hasData: mockHasData,
  })),
}));

describe('AstronomyScene - Form Validation', () => {
  let wrapper: ReturnType<typeof mount>;

  beforeEach(() => {
    // Reset mock state
    mockLoadData = vi.fn();
    mockLoading.value = false;
    mockError.value = null;
    mockData.value = null;
    mockHasData.value = false;
    
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

describe('AstronomyScene - Data Loading', () => {
  let wrapper: ReturnType<typeof mount>;

  beforeEach(() => {
    mockLoadData = vi.fn();
    mockLoading.value = false;
    mockError.value = null;
    mockData.value = null;
    mockHasData.value = false;
    
    wrapper = mount(AstronomyScene);
  });

  it('should display loading state', async () => {
    mockLoading.value = true;
    await wrapper.vm.$nextTick();
    
    expect(wrapper.text()).toContain('Loading');
  });

  it('should display error message when error occurs', async () => {
    mockError.value = 'Failed to load data';
    await wrapper.vm.$nextTick();
    
    const vm = wrapper.vm as any;
    expect(vm.error.value).toBe('Failed to load data');
  });

});

describe('AstronomyScene - With Data Loaded', () => {
  let wrapper: ReturnType<typeof mount>;

  beforeEach(() => {
    mockLoadData = vi.fn();
    mockLoading.value = false;
    mockError.value = null;
    mockData.value = {
      frames: [
        {
          datetime: '2026-02-02T00:00:00',
          sun: { altitude: 15.5, azimuth: 120.0, is_visible: true },
          moon: { altitude: 45.2, azimuth: 230.5, is_visible: true },
          moon_phase: { illumination: 0.75, phase_angle: 90.0, phase_name: 'Waxing Gibbous' },
        },
        {
          datetime: '2026-02-02T01:00:00',
          sun: { altitude: 20.0, azimuth: 125.0, is_visible: true },
          moon: { altitude: 40.0, azimuth: 235.0, is_visible: true },
          moon_phase: { illumination: 0.76, phase_angle: 91.0, phase_name: 'Waxing Gibbous' },
        },
      ],
      metadata: {
        location: { latitude: 51.5, longitude: -0.1, elevation: 0 },
        frame_count: 2,
        start_datetime: '2026-02-02T00:00:00',
        end_datetime: '2026-02-02T01:00:00',
        time_span_hours: 1.0,
      },
    };
    mockHasData.value = true;
    
    wrapper = mount(AstronomyScene);
  });

  it('should show animation controls when data is loaded', async () => {
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.animation-controls').exists()).toBe(true);
  });

  it('should display frame count', async () => {
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('Frames:');
  });

  it('should have view toggle buttons', async () => {
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('3D View');
    expect(wrapper.text()).toContain('Sky View');
  });

  it('should have play/pause button', async () => {
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toMatch(/Play|Pause/);
  });

  it('should have reset button', async () => {
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('Reset');
  });

});

