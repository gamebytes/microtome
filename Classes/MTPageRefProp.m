//
// microtome - Copyright 2012 Three Rings Design

#import "MTPageRefProp.h"

#import "MTPageRef.h"
#import "MTLibrary.h"

@implementation MTMutablePageRefProp

@synthesize pageType = _pageType;

- (id)initWithName:(NSString*)name parent:(id<MTPage>)parent nullable:(BOOL)nullable pageType:(Class)pageType {
    if ((self = [super initWithName:name parent:parent type:[MTMutablePageRef class] nullable:nullable])) {
        _pageType = pageType;
    }
    return self;
}

- (void)validateValue:(id)val {
    [super validateValue:val];
    MTMutablePageRef* ref = (MTMutablePageRef*)val;
    if (ref != nil && ![ref.pageType isSubclassOfClass:_pageType]) {
        [NSException raise:NSGenericException
                    format:@"Incompatible pageRef (pageType '%@' is not a subclass of '%@')",
         ref.pageType, _pageType];
    }
}

- (void)resolveRefs:(MTLibrary*)library {
    if (_value != nil) {
        MTMutablePageRef* ref = (MTMutablePageRef*)_value;
        ref.page = [library getPage:ref.pageName];
        if (ref.page == nil) {
            [NSException raise:NSGenericException
                format:@"Could not resolve PageRef [name=%@, pageName=%@]", self.name, ref.pageName];
        }
    }
}

@end
