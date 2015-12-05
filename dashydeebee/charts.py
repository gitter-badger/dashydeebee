import collections
import numbers
import svgwrite

import euclid

class Histogram(object):
    def __init__(self,
                 databbox = {'start': euclid.Point2(.2, .05),
                             'end': euclid.Point2(.95, .95)},
                 xtick = .1,
                 ytick = .1,
                 bar_width_factor = .9):
        self.databbox = databbox
        self.bar_width_factor = bar_width_factor
    
    def __call__(self, series):
        max_val = max([max(serie) for serie in series])
        m_norm = euclid.Matrix3().scale(1, 1 / max_val)
        
        t = self.databbox['start']
        s = self.databbox['end']-self.databbox['start']
        m_databox = euclid.Matrix3().translate(*t).scale(*s)
        
        ret = {}
        ret['bars'] = self.build_bars(m_databox * m_norm, series)
        ret['xaxis'] = [] #self.build_xaxis(series)
        return ret
    
    def build_xaxis(self, series):
        ret = {}
        ret['x1'] = 0
        ret['y1'] = 1
        ret['x2'] = 1
        ret['y2'] = 1
        return ret
    
    def build_bars(self, m, series):
        for serie in series:
            yield self.bars(m, serie)
    
    def bars(self, m, serie):
        interval_width = (1.0 / len(serie))
        bar_width = interval_width * self.bar_width_factor
        half_bar_width = bar_width / 2.0
                
        for x, y in zip(self.barsx(len(serie)), serie):
            x1 = x - half_bar_width
            y1 = 0.0
            x2 = x1 + bar_width
            y2 = y
            yield {'start': m * euclid.Point2(x1, y1),
                   'end': m * euclid.Point2(x2, y2)}
    
    def barsx(self, count):
        interval = 1.0 / count
        for i in range(count):
            yield interval / 2 + i * interval


class SVGHistogram(object):
    mat = euclid.Matrix3().scale(1.0, -1.0).translate(0, -1)
    mask = '{:.2f}%'
    
    def __call__(self, series):
        '''TODO: should use d3 chart standard'''
        dwg = svgwrite.Drawing()
        
        series = [range(1, 4)]
        chart = Histogram()(series)

        for i, bars in enumerate(chart['bars']):
            for bar in bars:
                b = self.rect(bar)
                b['class'] = 'dsdb-chart-bar'
                dwg.add(b)
        
        #r = self.rect({'start': euclid.Point2(.1, .5),
                       #'end': euclid.Point2(.4, .7)})
        #r['class'] = 'testbbox'
        #dwg.add(r)
        
        #l = self.line({'start': euclid.Point2(.1, .5),
                       #'end': euclid.Point2(.4, .7)})
        #l['class'] = 'dsbd-x'
        #dwg.add(l)
        
        #c = self.circle({'center': euclid.Point2(.1, .1),
                         #'r': .01})
        #dwg.add(c)
        
        #l = self.line({'start': euclid.Point2(.1, .1),
                       #'end': euclid.Point2(.2, .1)})
        #l['class'] = 'dsbd-x'
        #dwg.add(l)
        
        #l = self.line({'start': euclid.Point2(.1, .1),
                       #'end': euclid.Point2(.1, .2)})
        #l['class'] = 'dsbd-y'
        #dwg.add(l)
        
        #xaxis = chart['xaxis']
        #line = dwg.line((pc(xaxis['x1']), pc(xaxis['y1'])),
                        #(pc(xaxis['x2']), pc(xaxis['y2'])))
        #line['class'] = 'dsdb-chart-xaxis'
        #dwg.add(line)

        return dwg.tostring()

    def rect(self, rect):
        s = self.transform_point(rect['start'])
        e = self.transform_point(rect['end'])
        insert = euclid.Point2(min(s[0], e[0]),
                               min(s[1], e[1]))
        size = abs(e[0] - s[0]), abs(e[1] - s[1])
        transformed_insert = self.transform(tuple(insert))
        transformed_size = self.transform(size)
        return svgwrite.shapes.Rect(transformed_insert,
                                    transformed_size)
    
    def circle(self, circle):
        return svgwrite.shapes.Circle(**self.transform(circle))
    
    def line(self, line):
        return svgwrite.shapes.Line(**self.transform(line))

    def transform(self, val):
        if isinstance(val, str):
            return val
        
        if isinstance(val, euclid.Point2):
            return self.transform(self.transform_point(val))
        
        if isinstance(val, dict):
            return dict([(k, self.transform(v)) for k, v in val.items()])
        
        if isinstance(val, collections.Iterable):
            return tuple([self.transform(v) for v in val])
        
        return self.mask.format(val*100)
    
    def transform_point(self, point):
        return tuple(self.mat * point)


histogram = SVGHistogram()
